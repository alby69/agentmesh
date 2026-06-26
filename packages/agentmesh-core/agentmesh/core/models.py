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

class AgentReputation(BaseModel):
    """Represents the reputation of an agent in the mesh."""
    agent_id: str
    score: float = 0.0 # 0.0 to 1.0
    reviews_count: int = 0
    web_of_trust_depth: int = 1
    last_updated: float = Field(default_factory=time.time)

class KnowledgeFact(BaseModel):
    """A unit of shared knowledge in the mesh."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    subject: str
    predicate: str
    object: str
    source_agent: str
    confidence: float = 1.0
    timestamp: float = Field(default_factory=time.time)
