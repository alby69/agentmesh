"""Pydantic input and output contract schemas for AgentMesh Pro."""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class AgentQueryRequest(BaseModel):
    """Input contract for querying an agent or the mesh."""
    user_id: str = Field(..., description="Unique identifier of the user or system initiating the query")
    session_id: str = Field(..., description="Session ID for stateful conversation tracking")
    prompt: str = Field(..., description="The user query or instructions for the mesh")
    target_agent: Optional[str] = Field(default=None, description="Optional target agent capability or name")
    context: Dict[str, Any] = Field(default_factory=dict, description="Additional context parameters")
    require_human_approval: bool = Field(default=False, description="Flag indicating if workflow requires human approval")


class HumanApprovalDecision(BaseModel):
    """Contract for human-in-the-loop approval or rejection."""
    task_id: str = Field(..., description="Identifier of the task requiring approval")
    approved: bool = Field(..., description="Whether the proposed action was approved")
    feedback: Optional[str] = Field(default=None, description="Optional feedback or override instructions")


class AgentExecutionStep(BaseModel):
    """Step execution trace within the mesh."""
    step_id: str
    agent_name: str
    input_payload: Dict[str, Any]
    output_payload: Dict[str, Any]
    status: str = "success"
    execution_time_seconds: float = 0.0


class AgentQueryResponse(BaseModel):
    """Output contract for mesh responses."""
    session_id: str
    status: str = "completed"
    response_text: str
    steps: List[AgentExecutionStep] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    cached: bool = False


class HealthCheckResponse(BaseModel):
    """Health check output schema."""
    status: str = "ok"
    version: str = "0.1.0"
    services: Dict[str, str] = Field(default_factory=dict)
