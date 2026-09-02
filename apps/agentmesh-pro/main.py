"""FastAPI Web API Service and CLI entry point for AgentMesh Pro."""

import argparse
import sys
import uvicorn
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware

from agentmesh_pro.config import settings
from agentmesh_pro.schemas import (
    AgentQueryRequest,
    AgentQueryResponse,
    HealthCheckResponse,
    HumanApprovalDecision,
)
from agentmesh_pro.orchestrator import orchestrator
from agentmesh_pro.persistence import cache_manager, memory_store
from agentmesh_pro.gateway import gateway

app = FastAPI(
    title=settings.app_name,
    version=settings.version,
    description="Enterprise Multi-Agent Mesh System with LangGraph, PGVector, Redis, and LiteLLM",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", response_model=HealthCheckResponse, tags=["System"])
async def health_check():
    """Returns application health and subsystem statuses."""
    postgres_status = "connected" if memory_store._db_connected else "offline_fallback"
    redis_status = "connected" if cache_manager._redis_client else "in_memory_fallback"

    return HealthCheckResponse(
        status="ok",
        version=settings.version,
        services={
            "postgres_pgvector": postgres_status,
            "redis_cache": redis_status,
            "model_gateway": f"active ({gateway.default_model})",
            "orchestrator": "langgraph_ready",
        },
    )


@app.post("/api/v1/query", response_model=AgentQueryResponse, tags=["Mesh Execution"])
async def execute_agent_query(request: AgentQueryRequest):
    """Executes a query through the AgentMesh Pro orchestrator."""
    try:
        response = await orchestrator.execute_query(request)
        return response
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AgentMesh execution error: {str(e)}",
        )


@app.post("/api/v1/approval", response_model=AgentQueryResponse, tags=["Governance"])
async def submit_human_approval(decision: HumanApprovalDecision):
    """Processes human approval or rejection decision for a pending workflow."""
    # Retrieve pending request from cache/session
    cached_prompt = cache_manager.get(f"approval_pending:{decision.task_id}")
    prompt = cached_prompt or f"Pending task {decision.task_id}"

    request = AgentQueryRequest(
        user_id="human_approver",
        session_id=decision.task_id,
        prompt=prompt,
        require_human_approval=True,
    )

    state = {
        "user_id": request.user_id,
        "session_id": request.session_id,
        "prompt": request.prompt,
        "target_agent": None,
        "context": {},
        "require_human_approval": True,
        "is_approved": decision.approved,
        "feedback": decision.feedback,
        "current_step": "approval_processed",
        "steps": [],
        "final_response": "",
        "error": None,
    }

    if decision.approved:
        state = await orchestrator._node_agent_execution(state)
    state = orchestrator._node_postprocess(state)

    return AgentQueryResponse(
        session_id=decision.task_id,
        status="approved_and_executed" if decision.approved else "rejected",
        response_text=state.get("final_response", ""),
        metadata={"human_feedback": decision.feedback},
    )


def main():
    parser = argparse.ArgumentParser(description="AgentMesh Pro - Enterprise Production AI Agent System")
    parser.add_argument("--server", action="store_true", help="Start FastAPI web server")
    parser.add_argument("--host", type=str, default=settings.host, help="Host address to bind")
    parser.add_argument("--port", type=int, default=settings.port, help="Port to bind")
    args = parser.parse_args()

    if args.server:
        print(f"Starting {settings.app_name} on {args.host}:{args.port}")
        uvicorn.run("main:app", host=args.host, port=args.port, reload=settings.debug)
    else:
        print(f"{settings.app_name} v{settings.version}")
        print("Use --server to start the API server.")


if __name__ == "__main__":
    main()
