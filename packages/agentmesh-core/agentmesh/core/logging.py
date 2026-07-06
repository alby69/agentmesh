import logging
import sys
import json
from datetime import datetime
from typing import Any, Dict

class StructuredFormatter(logging.Formatter):
    """
    JSON formatter for structured logging.
    """
    def format(self, record: logging.LogRecord) -> str:
        log_record: Dict[str, Any] = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "func": record.funcName,
        }
        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)

        # Add extra fields if they exist
        if hasattr(record, "extra_fields"):
            log_record.update(record.extra_fields)

        return json.dumps(log_record)

def setup_logging(level: int = logging.INFO, structured: bool = False):
    """
    Set up global logging configuration.
    """
    handler = logging.StreamHandler(sys.stdout)
    if structured:
        handler.setFormatter(StructuredFormatter())
    else:
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    # Remove existing handlers
    for h in root_logger.handlers[:]:
        root_logger.removeHandler(h)
    root_logger.addHandler(handler)

def get_logger(name: str) -> logging.Logger:
    """
    Get a logger with the given name.
    """
    return logging.getLogger(name)
