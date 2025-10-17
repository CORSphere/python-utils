"""
Utilities for structured logging with correlation IDs.
"""
from typing import Optional
from contextvars import ContextVar

correlation_id_var: ContextVar[Optional[str]] = ContextVar('correlation_id', default=None)
request_path_var: ContextVar[Optional[str]] = ContextVar('request_path', default=None)
request_method_var: ContextVar[Optional[str]] = ContextVar('request_method', default=None)


def set_correlation_id(correlation_id: Optional[str]) -> None:
  """Set the correlation ID for the current context."""
  correlation_id_var.set(correlation_id)

def get_correlation_id() -> Optional[str]:
  """Get the correlation ID from the current context."""
  return correlation_id_var.get()


def set_request_context(path: Optional[str], method: Optional[str]) -> None:
  """Set the request path and method for the current context."""
  request_path_var.set(path)
  request_method_var.set(method)


def get_request_path() -> Optional[str]:
  """Get the request path from the current context."""
  return request_path_var.get()


def get_request_method() -> Optional[str]:
  """Get the request method from the current context."""
  return request_method_var.get()
