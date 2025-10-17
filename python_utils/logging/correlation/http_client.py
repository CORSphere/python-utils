"""
A http client wrapper that adds correlation IDs to outgoing requests.
"""

from .correlation import get_correlation_id
import requests
from uuid import uuid4
 
def _requests(method: str, url: str, **kwargs):
  # Add the correlation ID to headers if not already present
  headers = kwargs.get("headers", {})
  correlation_id = headers.get('x-correlation-id')
  if not correlation_id:
    correlation_id = get_correlation_id() or uuid4()
    headers["x-correlation-id"] = correlation_id

  return requests.request(method, url, headers=headers, **kwargs)

def post(url: str, **kwargs):
  return _requests("post", url, **kwargs)

def get(url: str, **kwargs):
  return _requests("get", url, **kwargs)