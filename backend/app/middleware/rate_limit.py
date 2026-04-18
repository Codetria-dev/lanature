"""
Rate limiting middleware for FastAPI application.

Protects against brute force attacks on authentication endpoints.
Uses slowapi for efficient rate limiting based on IP address.
"""

from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request
from fastapi.responses import JSONResponse

# Initialize limiter with get_remote_address to identify clients by IP
limiter = Limiter(key_func=get_remote_address, default_limits=["100/minute"])


async def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded) -> JSONResponse:
    """
    Custom error handler for rate limit exceeded.

    Returns 429 Too Many Requests with appropriate message.
    """
    return JSONResponse(
        status_code=429,
        content={
            "detail": "Too many requests. Please try again later.",
            "retry_after": exc.detail if hasattr(exc, "detail") else None
        }
    )


# Rate limit definitions for specific endpoints
RATE_LIMITS = {
    "login": "5/minute",  # 5 login attempts per minute per IP
    "register": "3/hour",  # 3 registration attempts per hour per IP
    "verify_2fa": "10/minute",  # 10 2FA verification attempts per minute
    "get_token": "100/minute",  # General token refresh limit
    "default": "100/minute",  # Default limit for other endpoints
}
