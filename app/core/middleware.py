"""FastAPI middleware for request/response logging."""
import time
import uuid
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request
from loguru import logger


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to log all requests and responses with structured data."""
    
    async def dispatch(self, request: Request, call_next):
        """Process request and response with logging."""
        # Generate unique request ID
        request_id = str(uuid.uuid4())
        
        # Add request ID to request state
        request.state.request_id = request_id
        
        # Log request details
        logger.bind(request_id=request_id).info(
            "Incoming request",
            method=request.method,
            path=request.url.path,
            query_params=dict(request.query_params),
            client=request.client.host if request.client else None,
        )
        
        # Track request time
        start_time = time.time()
        
        try:
            response = await call_next(request)
            
            # Calculate response time
            process_time = time.time() - start_time
            
            # Log response details
            logger.bind(request_id=request_id).info(
                "Response sent",
                method=request.method,
                path=request.url.path,
                status_code=response.status_code,
                process_time_ms=f"{process_time * 1000:.2f}",
            )
            
            # Add custom header with request ID
            response.headers["X-Request-ID"] = request_id
            
            return response
            
        except Exception as exc:
            process_time = time.time() - start_time
            
            # Log error
            logger.bind(request_id=request_id).error(
                "Request processing error",
                method=request.method,
                path=request.url.path,
                error=str(exc),
                process_time_ms=f"{process_time * 1000:.2f}",
            )
            raise
