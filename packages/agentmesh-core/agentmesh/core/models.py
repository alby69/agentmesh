from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, ConfigDict
import uuid
import time

class AgentCapability(BaseModel):
    """Represents a set of skills and metadata published by an agent."""
    agent_id: str
    name: str
    description: str
    version: str
    public_key: str
    capabilities: List[str]
    metadata: Dict[str, Any] = Field(default_factory=dict)

class AgentMessage(BaseModel):
    """Standardized message for inter-agent communication."""
    model_config = ConfigDict(populate_by_name=True)

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    sender: str  # Public key of the sender
    receiver: Optional[str] = None  # Public key of the receiver (None for broadcast)
    message_type: str = Field(alias="type") # 'task', 'response', 'info', etc.
    payload: Dict[str, Any]
    timestamp: float = Field(default_factory=time.time)
    signature: Optional[str] = None
