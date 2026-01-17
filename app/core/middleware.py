"""FastAPI middleware for request/response logging with correlation ID."""
import time
import uuid
from typing import Callable
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from loguru import logger
from app.core.correlation_id import set_correlation_id, get_correlation_id


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to log all requests and responses with correlation ID tracking."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and response with correlation ID logging."""
        # Extract correlation ID from request headers or generate new one
        correlation_id_header = "X-Correlation-ID"
        request_correlation_id = (
            request.headers.get(correlation_id_header)
            or request.headers.get("X-Request-ID")
            or str(uuid.uuid4())
        )
        
        # Add correlation ID to request state for access in endpoints
        request.state.correlation_id = request_correlation_id
        request.state.request_id = request_correlation_id  # Backward compatibility
        
        # Set correlation ID in context for the correlation_id module
        set_correlation_id(request_correlation_id)
        
        # Log request details with correlation ID
        logger.bind(
            correlation_id=request_correlation_id,
            request_id=request_correlation_id,
        ).info(
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
            
            # Log response details with correlation ID
            logger.bind(
                correlation_id=request_correlation_id,
                request_id=request_correlation_id,
            ).info(
                "Response sent",
                method=request.method,
                path=request.url.path,
                status_code=response.status_code,
                process_time_ms=f"{process_time * 1000:.2f}",
            )
            
            # Add correlation ID headers to response
            response.headers[correlation_id_header] = request_correlation_id
            response.headers["X-Request-ID"] = request_correlation_id
            
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
