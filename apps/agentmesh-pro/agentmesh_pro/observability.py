"""Langfuse observability and tracing integration for AgentMesh Pro."""

import logging
from typing import Any, Dict, Optional
from agentmesh_pro.config import settings

logger = logging.getLogger(__name__)


class ObservabilityTracer:
    """Langfuse tracer with graceful offline fallback."""

    def __init__(self):
        self._client = None
        self._init_langfuse()

    def _init_langfuse(self):
        if settings.langfuse_public_key and settings.langfuse_secret_key:
            try:
                from langfuse import Langfuse
                self._client = Langfuse(
                    public_key=settings.langfuse_public_key,
                    secret_key=settings.langfuse_secret_key,
                    host=settings.langfuse_host,
                )
                logger.info("Langfuse observability initialized.")
            except Exception as e:
                logger.warning(f"Could not initialize Langfuse: {e}")
                self._client = None

    def trace_execution(
        self,
        name: str,
        user_id: str,
        session_id: str,
        input_data: Dict[str, Any],
        output_data: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None,
        duration_seconds: float = 0.0,
    ):
        """Records an execution trace step in Langfuse or logs locally."""
        metadata = metadata or {}
        if self._client:
            try:
                trace = self._client.trace(
                    name=name,
                    user_id=user_id,
                    session_id=session_id,
                    metadata=metadata,
                )
                trace.span(
                    name=f"{name}_span",
                    input=input_data,
                    output=output_data,
                    metadata={"duration": duration_seconds},
                )
                logger.info(f"Langfuse trace recorded for session {session_id}")
                return
            except Exception as e:
                logger.warning(f"Failed to record Langfuse trace: {e}")

        # Local structured log tracing fallback
        logger.info(
            f"[Observability Trace] name={name} user_id={user_id} session_id={session_id} "
            f"duration={duration_seconds:.3f}s input={input_data} output={output_data}"
        )


tracer = ObservabilityTracer()
