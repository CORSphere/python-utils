from fastapi import Request
from fastapi.responses import JSONResponse, Response
from starlette.middleware.base import BaseHTTPMiddleware, _StreamingResponse
from typing import Callable, Dict, Optional, Any
import logging
import json
from uuid import uuid4

from .correlation import set_correlation_id, set_request_context


logger = logging.getLogger(__name__)


class CorrelationMiddleware(BaseHTTPMiddleware):
    """
    Middleware to extract x-correlation-id from request headers
    and make it available throughout the request lifecycle for tracking logs.
    """

    async def dispatch(self, request: Request, call_next: Callable):
        try:
            correlation_id = request.headers.get('x-correlation-id')
            path = request.url.path
            method = request.method

            if not correlation_id:
                correlation_id = str(uuid4())
            
            set_correlation_id(correlation_id)
            set_request_context(path, method)

            logger.info(f"Incoming request - {method} {path}")

            response: _StreamingResponse = await call_next(request)
            status_code = response.status_code
            is_error_response = status_code < 200 or status_code >= 400
            
            if is_error_response:
                return await self.handle_error_response(request, response)

            logger.info(
                f"Request succeeded - {method} {path} - Status: {status_code}"
            )
            return response
            
        except Exception as e:
            logger.error(
                f"Unexpected Server Error: {str(e)}",
                exc_info=True,
            )
            return JSONResponse(
                content=str(e),
                status_code=500,
            )

    async def handle_error_response(self, request: Request, response: _StreamingResponse) -> JSONResponse:
        response_body = await self.read_response_body(response)
        error_detail = self.parse_response_as_json(response_body)
        self.log_error_response(
            method=request.method, 
            path=request.url.path, 
            error_detail=error_detail, 
        )
        return JSONResponse(
            content=error_detail,
            status_code=response.status_code,
            headers=dict(response.headers),
            media_type=response.media_type
        )

    async def read_response_body(self, response: _StreamingResponse) -> bytes:
        response_body = b""
        async for chunk in response.body_iterator:
            response_body += chunk
        return response_body

    def parse_response_as_json(self, response_body: bytes) -> Optional[Dict[str, Any]]:
        try:
            return json.loads(response_body.decode())
        except (json.JSONDecodeError, UnicodeDecodeError):
            return None
    
    def log_error_response(
        self,
        method: str,
        path: str,
        error_detail: Optional[Dict[str, Any]],
    ) -> None:
        logger.error(f"Request failed - {method} {path} - {str(error_detail)}")
