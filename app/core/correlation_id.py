"""Correlation ID context management for request tracing."""
import contextvars
from typing import Optional

# Context variable to store correlation ID across async contexts
_correlation_id_var: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar("correlation_id", default=None)


def set_correlation_id(correlation_id: str) -> None:
    """Set correlation ID in context."""
    _correlation_id_var.set(correlation_id)


def get_correlation_id() -> Optional[str]:
    """Get correlation ID from context."""
    return _correlation_id_var.get()


def reset_correlation_id() -> None:
    """Reset correlation ID in context."""
    _correlation_id_var.set(None)
