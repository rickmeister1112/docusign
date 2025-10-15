"""
Custom middleware for the application.
"""
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
import time
from .logging_config import log_api_request


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware to log all API requests with timing and user info.
    """
    
    async def dispatch(self, request: Request, call_next):
        # Start timer
        start_time = time.time()
        
        # Get user email from token if authenticated
        user_email = None
        auth_header = request.headers.get("authorization")
        if auth_header and auth_header.startswith("Bearer "):
            # We have a token but won't decode it here (too expensive)
            # Just mark as authenticated
            user_email = "authenticated"
        
        # Process request
        response = await call_next(request)
        
        # Calculate duration
        duration_ms = (time.time() - start_time) * 1000
        
        # Log request
        log_api_request(
            method=request.method,
            path=str(request.url.path),
            status_code=response.status_code,
            duration_ms=round(duration_ms, 2),
            user_email=user_email
        )
        
        return response

