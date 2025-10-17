"""
Custom JSON logging formatter and utilities for structured logging.
"""
import json
import logging
from datetime import datetime, timezone
from typing import Any, Dict
from ..correlation.correlation import get_correlation_id, get_request_path, get_request_method

class JSONFormatter(logging.Formatter):
  """
  Custom JSON formatter for structured logging.
  """
  
  def __init__(self, service_name: str):
    super().__init__()
    self.service_name = service_name
  
  def format(self, record: logging.LogRecord) -> str:
    log_data: Dict[str, Any] = {
      "timestamp": datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(),
      "level": record.levelname,
      "service": self.service_name,
    }
    
    correlation_id = get_correlation_id()
    if correlation_id:
      log_data["correlationId"] = correlation_id
    
    request_path = get_request_path()
    if request_path:
      log_data["path"] = request_path
    
    request_method = get_request_method()
    if request_method:
      log_data["method"] = request_method
    
    log_data["message"] = record.getMessage()

    context = f'{record.__dict__.get("pathname", "")}:{record.__dict__.get("lineno", "")}'
    log_data["context"] = context
    
    # Exclude redundant and irrelevant attributes of LogRecord to keep only relevant metadata in the logs
    excluded_log_attributes = {
      'name', 'msg', 'args', 'created', 'filename', 'funcName',
      'levelname', 'levelno', 'lineno', 'module', 'msecs',
      'message', 'pathname', 'process', 'processName',
      'relativeCreated', 'thread', 'threadName', 'exc_info',
      'exc_text', 'stack_info', 'taskName'
    }
    
    log_data["extra"] = {}
    extra_fields = {
      k: v 
      for k, v in record.__dict__.items()
      if k not in excluded_log_attributes
    }
    
    if extra_fields:
      log_data["extra"] = extra_fields
    
    if record.exc_info:
      log_data['extra']["error"] = self.formatException(record.exc_info)
    
    return json.dumps(log_data)
