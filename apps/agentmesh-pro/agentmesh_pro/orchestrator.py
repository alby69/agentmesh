"""LangGraph orchestration layer for AgentMesh Pro multi-agent execution."""

import time
import logging
from typing import Any, Dict, List, Optional, TypedDict

from agentmesh_pro.gateway import gateway
from agentmesh_pro.persistence import cache_manager, memory_store
from agentmesh_pro.observability import tracer
from agentmesh_pro.schemas import AgentExecutionStep, AgentQueryRequest, AgentQueryResponse

logger = logging.getLogger(__name__)


class MeshState(TypedDict):
    """LangGraph state dict representing workflow context."""
    user_id: str
    session_id: str
    prompt: str
    target_agent: Optional[str]
    context: Dict[str, Any]
    require_human_approval: bool
    is_approved: Optional[bool]
    feedback: Optional[str]
    current_step: str
    steps: List[Dict[str, Any]]
    final_response: str
    error: Optional[str]


class MeshOrchestrator:
    """Orchestrates multi-agent mesh workflows using LangGraph state graphs."""

    def __init__(self):
        self._graph = None
        self._setup_langgraph()

    def _setup_langgraph(self):
        try:
            from langgraph.graph import StateGraph, END

            workflow = StateGraph(MeshState)

            # Define graph nodes
            workflow.add_node("preprocess", self._node_preprocess)
            workflow.add_node("agent_execution", self._node_agent_execution)
            workflow.add_node("human_approval_gate", self._node_human_approval_gate)
            workflow.add_node("postprocess", self._node_postprocess)

            # Define edges and conditional routing
            workflow.set_entry_point("preprocess")
            workflow.add_edge("preprocess", "human_approval_gate")

            workflow.add_conditional_edges(
                "human_approval_gate",
                self._check_approval_needed,
                {
                    "proceed": "agent_execution",
                    "await_approval": END,
                    "rejected": "postprocess",
                },
            )

            workflow.add_edge("agent_execution", "postprocess")
            workflow.add_edge("postprocess", END)

            self._graph = workflow.compile()
            logger.info("LangGraph workflow compiled successfully.")
        except Exception as e:
            logger.warning(f"Could not initialize LangGraph StateGraph ({e}). Using direct orchestrator execution.")
            self._graph = None

    def _node_preprocess(self, state: MeshState) -> MeshState:
        """Loads historical context from Redis/PGVector memory."""
        start_time = time.time()
        session_id = state["session_id"]
        query = state["prompt"]

        # Check cache
        cached = cache_manager.get(f"query:{session_id}:{query}")
        if cached:
            state["final_response"] = cached
            state["current_step"] = "cached"
            return state

        # Search memory
        retrieved_memories = memory_store.search_memory(session_id, query)
        state["context"]["memory_records"] = retrieved_memories
        state["current_step"] = "preprocessed"

        step_record = {
            "step_id": "step_preprocess",
            "agent_name": "MemoryRetrieverAgent",
            "input_payload": {"session_id": session_id, "query": query},
            "output_payload": {"retrieved_count": len(retrieved_memories)},
            "status": "success",
            "execution_time_seconds": round(time.time() - start_time, 4),
        }
        state["steps"].append(step_record)
        return state

    def _node_human_approval_gate(self, state: MeshState) -> MeshState:
        """Handles Human-in-the-loop approval routing."""
        if state.get("require_human_approval") and state.get("is_approved") is None:
            state["current_step"] = "awaiting_human_approval"
            state["final_response"] = "Task requires human approval before proceeding."
        return state

    def _check_approval_needed(self, state: MeshState) -> str:
        if state.get("require_human_approval"):
            if state.get("is_approved") is True:
                return "proceed"
            elif state.get("is_approved") is False:
                return "rejected"
            else:
                return "await_approval"
        return "proceed"

    async def _node_agent_execution(self, state: MeshState) -> MeshState:
        """Executes agent generation via ModelGateway."""
        start_time = time.time()
        prompt = state["prompt"]
        context_memories = state["context"].get("memory_records", [])

        messages = [
            {"role": "system", "content": f"You are AgentMesh Pro Core Agent. Context: {context_memories}"},
            {"role": "user", "content": prompt},
        ]

        gateway_result = await gateway.generate_response(messages)
        state["final_response"] = gateway_result["content"]
        state["current_step"] = "executed"

        step_record = {
            "step_id": "step_agent_exec",
            "agent_name": state.get("target_agent") or "CoreMeshAgent",
            "input_payload": {"prompt": prompt},
            "output_payload": gateway_result,
            "status": gateway_result.get("status", "success"),
            "execution_time_seconds": round(time.time() - start_time, 4),
        }
        state["steps"].append(step_record)

        # Cache result
        cache_manager.set(f"query:{state['session_id']}:{prompt}", gateway_result["content"])
        # Store in long term memory
        memory_store.store_memory(state["session_id"], f"query_{time.time()}", gateway_result["content"])

        return state

    def _node_postprocess(self, state: MeshState) -> MeshState:
        """Finalizes response and records observability trace."""
        if state.get("is_approved") is False:
            state["final_response"] = f"Execution rejected by human operator. Feedback: {state.get('feedback', 'None')}"

        tracer.trace_execution(
            name="mesh_workflow",
            user_id=state["user_id"],
            session_id=state["session_id"],
            input_data={"prompt": state["prompt"], "target_agent": state.get("target_agent")},
            output_data={"response": state["final_response"], "status": state["current_step"]},
            metadata={"steps_count": len(state["steps"])},
        )
        return state

    async def execute_query(self, request: AgentQueryRequest) -> AgentQueryResponse:
        """Runs the query request through the orchestrator workflow."""
        start_time = time.time()
        initial_state: MeshState = {
            "user_id": request.user_id,
            "session_id": request.session_id,
            "prompt": request.prompt,
            "target_agent": request.target_agent,
            "context": request.context,
            "require_human_approval": request.require_human_approval,
            "is_approved": None,
            "feedback": None,
            "current_step": "init",
            "steps": [],
            "final_response": "",
            "error": None,
        }

        if self._graph:
            try:
                final_state = await self._graph.ainvoke(initial_state)
            except Exception as e:
                logger.warning(f"LangGraph execution fallback to direct runner: {e}")
                final_state = await self._execute_direct(initial_state)
        else:
            final_state = await self._execute_direct(initial_state)

        steps_obj = [AgentExecutionStep(**s) for s in final_state.get("steps", [])]
        return AgentQueryResponse(
            session_id=request.session_id,
            status=final_state.get("current_step", "completed"),
            response_text=final_state.get("final_response", ""),
            steps=steps_obj,
            metadata={"execution_time": round(time.time() - start_time, 4)},
        )

    async def _execute_direct(self, state: MeshState) -> MeshState:
        """Direct fallback execution when LangGraph state graph is not active."""
        state = self._node_preprocess(state)
        if state.get("current_step") == "cached":
            return state

        state = self._node_human_approval_gate(state)
        approval_route = self._check_approval_needed(state)

        if approval_route == "proceed":
            state = await self._node_agent_execution(state)
            state = self._node_postprocess(state)
        elif approval_route == "rejected":
            state = self._node_postprocess(state)

        return state


orchestrator = MeshOrchestrator()
