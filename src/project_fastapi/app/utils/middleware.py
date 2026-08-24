from fastapi.requests import Request
from fastapi.responses import Response
from ..core import logger
from uuid import uuid4
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
import time
import asyncio

class CustomLogging(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        request_id = str(uuid4())
        start_time = time.time()
        
        response = await call_next(request)
        process_time = time.time() - start_time
        
        process_time_str = f"{process_time:.4f}s"
        
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time"] = process_time_str
        
        logger.info(
            f"RequestID: {request_id} | "
            f"Method: {request.method} | "
            f"Path: {request.url.path} | "
            f"Status: {response.status_code} | "
            f"ProcessTime: {process_time_str}"
        )
        return response