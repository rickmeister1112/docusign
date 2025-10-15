"""
Logging configuration for the application.
Provides structured logging for monitoring and debugging.
"""
import logging
import sys
from datetime import datetime
import json


class JSONFormatter(logging.Formatter):
    """
    Custom formatter that outputs JSON structured logs.
    Makes logs easily parseable by log aggregation tools.
    """
    
    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        # Add extra fields if present
        if hasattr(record, "extra_data"):
            log_data.update(record.extra_data)
        
        return json.dumps(log_data)


def setup_logging(log_level: str = "INFO") -> logging.Logger:
    """
    Setup application logging with JSON formatter.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    
    Returns:
        Configured logger instance
    """
    # Create logger
    logger = logging.getLogger("feedback_app")
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Remove existing handlers
    logger.handlers = []
    
    # Create console handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    
    # Set JSON formatter
    formatter = JSONFormatter()
    handler.setFormatter(formatter)
    
    # Add handler to logger
    logger.addHandler(handler)
    
    return logger


# Create application logger
app_logger = setup_logging()


def log_auth_attempt(email: str, success: bool, ip_address: str = "unknown") -> None:
    """
    Log authentication attempts for security monitoring.
    
    Args:
        email: User email attempting authentication
        success: Whether authentication was successful
        ip_address: IP address of the request
    """
    extra = {
        "extra_data": {
            "event_type": "auth_attempt",
            "email": email,
            "success": success,
            "ip_address": ip_address,
        }
    }
    
    if success:
        app_logger.info("Successful authentication", extra=extra)
    else:
        app_logger.warning("Failed authentication attempt", extra=extra)


def log_api_request(
    method: str,
    path: str,
    status_code: int,
    duration_ms: float,
    user_email: str = None
) -> None:
    """
    Log API requests for monitoring and debugging.
    
    Args:
        method: HTTP method
        path: Request path
        status_code: Response status code
        duration_ms: Request duration in milliseconds
        user_email: Authenticated user email (if any)
    """
    extra = {
        "extra_data": {
            "event_type": "api_request",
            "method": method,
            "path": path,
            "status_code": status_code,
            "duration_ms": duration_ms,
            "user_email": user_email,
        }
    }
    
    app_logger.info("API request", extra=extra)


def log_error(
    error_type: str,
    error_message: str,
    stack_trace: str = None,
    **kwargs
) -> None:
    """
    Log application errors with context.
    
    Args:
        error_type: Type of error
        error_message: Error message
        stack_trace: Stack trace (if available)
        **kwargs: Additional context
    """
    extra = {
        "extra_data": {
            "event_type": "error",
            "error_type": error_type,
            "stack_trace": stack_trace,
            **kwargs
        }
    }
    
    app_logger.error(error_message, extra=extra)

