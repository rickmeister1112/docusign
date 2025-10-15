"""
Rate limiting configuration using slowapi.
Protects API endpoints from abuse and DDoS attacks.
"""
from slowapi import Limiter
from slowapi.util import get_remote_address


# Create limiter instance that tracks by IP address
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["60/minute"]  # Default: 60 requests per minute
)


def rate_limit_auth():
    """
    Strict rate limit for authentication endpoints.
    Prevents brute force attacks on login/register.
    
    Returns: 5 requests per minute per IP
    """
    return "5/minute"


def rate_limit_write():
    """
    Moderate rate limit for write operations.
    Prevents spam feedback submissions.
    
    Returns: 20 requests per minute per IP
    """
    return "20/minute"


def rate_limit_read():
    """
    Permissive rate limit for read operations.
    Allows normal browsing while preventing abuse.
    
    Returns: 100 requests per minute per IP
    """
    return "100/minute"

