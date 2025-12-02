"""Error handling middleware for Core API."""

from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import time

from shared.utils.exceptions import TubeWikiException
from shared.utils.logger import get_logger

logger = get_logger(__name__)


async def error_handler_middleware(request: Request, call_next):
    """
    Global error handler middleware.
    
    Catches all exceptions and returns appropriate JSON responses.
    """
    start_time = time.time()
    
    try:
        response = await call_next(request)
        return response
        
    except TubeWikiException as e:
        # Custom application exceptions
        duration_ms = (time.time() - start_time) * 1000
        
        logger.error(
            f"TubeWiki error: {e.message}",
            extra={
                "status_code": e.status_code,
                "path": request.url.path,
                "method": request.method,
                "duration_ms": duration_ms,
                "details": e.details
            }
        )
        
        return JSONResponse(
            status_code=e.status_code,
            content={
                "error": {
                    "type": type(e).__name__,
                    "message": e.message,
                    "details": e.details
                }
            }
        )
    
    except RequestValidationError as e:
        # Pydantic validation errors
        duration_ms = (time.time() - start_time) * 1000
        
        logger.warning(
            f"Validation error: {str(e)}",
            extra={
                "path": request.url.path,
                "method": request.method,
                "duration_ms": duration_ms
            }
        )
        
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "error": {
                    "type": "ValidationError",
                    "message": "Request validation failed",
                    "details": {"errors": e.errors()}
                }
            }
        )
    
    except StarletteHTTPException as e:
        # HTTP exceptions
        duration_ms = (time.time() - start_time) * 1000
        
        logger.warning(
            f"HTTP error: {e.detail}",
            extra={
                "status_code": e.status_code,
                "path": request.url.path,
                "method": request.method,
                "duration_ms": duration_ms
            }
        )
        
        return JSONResponse(
            status_code=e.status_code,
            content={
                "error": {
                    "type": "HTTPException",
                    "message": e.detail
                }
            }
        )
    
    except Exception as e:
        # Unexpected errors
        duration_ms = (time.time() - start_time) * 1000
        
        logger.error(
            f"Unexpected error: {str(e)}",
            extra={
                "path": request.url.path,
                "method": request.method,
                "duration_ms": duration_ms
            },
            exc_info=True
        )
        
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": {
                    "type": "InternalServerError",
                    "message": "An unexpected error occurred"
                }
            }
        )
