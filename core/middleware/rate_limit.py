"""Rate limiting middleware for Core API."""

from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request
from fastapi.responses import JSONResponse

from shared.utils.logger import get_logger

logger = get_logger(__name__)

# Create limiter instance
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["100/minute"],
    storage_uri="memory://",  # Use Redis in production: "redis://localhost:6379"
)


def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded) -> JSONResponse:
    """
    Custom handler for rate limit exceeded errors.
    """
    logger.warning(
        f"Rate limit exceeded",
        extra={
            "path": request.url.path,
            "method": request.method,
            "client": get_remote_address(request),
            "limit": exc.detail
        }
    )
    
    return JSONResponse(
        status_code=429,
        content={
            "error": {
                "type": "RateLimitExceeded",
                "message": "Too many requests",
                "details": {
                    "limit": exc.detail,
                    "retry_after": "60 seconds"
                }
            }
        },
        headers={"Retry-After": "60"}
    )
