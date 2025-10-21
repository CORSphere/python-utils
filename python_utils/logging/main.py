from fastapi import FastAPI
import logging
from .correlation.middleware import CorrelationMiddleware
from .formatter import JSONFormatter
import os, sys

def configure_logging(app: FastAPI, service_name: str):
  """
  Configure logging for FastAPI application with correlation middleware and JSON formatting.
  """
  try:
    if not app:
      raise ValueError("FastAPI app instance must be provided for logging configuration.")
    if not service_name:
      raise ValueError("Service name must be provided for logging configuration.")
    
    app.add_middleware(CorrelationMiddleware)
    
    json_handler = logging.StreamHandler(sys.stdout)
    json_handler.setFormatter(JSONFormatter(service_name=service_name))

    logging.basicConfig(
      level=os.getenv("LOG_LEVEL", "INFO").upper(),
      handlers=[json_handler],
      force=True,
    )

    for name in ("uvicorn", "uvicorn.error", "uvicorn.access"):
      lg = logging.getLogger(name)
      lg.handlers.clear()
      lg.addHandler(json_handler)
      lg.propagate = False
  except ValueError as value_err:
    raise value_err
  except Exception as e:
    raise RuntimeError(f"Failed to configure logging: {str(e)}") from e