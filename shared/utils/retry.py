"""Retry utilities for Worker service."""

import asyncio
from typing import Callable, TypeVar, Optional
from functools import wraps

from shared.utils.logger import get_logger
from shared.utils.exceptions import ExternalServiceError

logger = get_logger(__name__)

T = TypeVar('T')


async def retry_with_backoff(
    func: Callable[..., T],
    max_retries: int = 3,
    initial_delay: float = 1.0,
    max_delay: float = 60.0,
    backoff_factor: float = 2.0,
    exceptions: tuple = (Exception,)
) -> T:
    """
    Retry a function with exponential backoff.
    
    Args:
        func: Async function to retry
        max_retries: Maximum number of retry attempts
        initial_delay: Initial delay in seconds
        max_delay: Maximum delay in seconds
        backoff_factor: Multiplier for delay after each retry
        exceptions: Tuple of exceptions to catch and retry
        
    Returns:
        Result of the function
        
    Raises:
        Last exception if all retries fail
    """
    delay = initial_delay
    last_exception = None
    
    for attempt in range(max_retries + 1):
        try:
            if asyncio.iscoroutinefunction(func):
                return await func()
            else:
                return func()
                
        except exceptions as e:
            last_exception = e
            
            if attempt == max_retries:
                logger.error(
                    f"All {max_retries} retries failed for {func.__name__}",
                    extra={"error": str(e)}
                )
                raise
            
            logger.warning(
                f"Retry {attempt + 1}/{max_retries} for {func.__name__}",
                extra={
                    "error": str(e),
                    "delay": delay
                }
            )
            
            await asyncio.sleep(delay)
            delay = min(delay * backoff_factor, max_delay)
    
    raise last_exception


def with_retry(
    max_retries: int = 3,
    initial_delay: float = 1.0,
    backoff_factor: float = 2.0,
    exceptions: tuple = (ExternalServiceError,)
):
    """
    Decorator for retrying async functions with exponential backoff.
    
    Usage:
        @with_retry(max_retries=3, initial_delay=1.0)
        async def fetch_data():
            ...
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            async def _func():
                return await func(*args, **kwargs)
            
            return await retry_with_backoff(
                _func,
                max_retries=max_retries,
                initial_delay=initial_delay,
                backoff_factor=backoff_factor,
                exceptions=exceptions
            )
        
        return wrapper
    return decorator


async def with_timeout(
    func: Callable[..., T],
    timeout_seconds: float,
    timeout_message: Optional[str] = None
) -> T:
    """
    Execute a function with a timeout.
    
    Args:
        func: Async function to execute
        timeout_seconds: Timeout in seconds
        timeout_message: Optional custom timeout message
        
    Returns:
        Result of the function
        
    Raises:
        asyncio.TimeoutError: If function exceeds timeout
    """
    try:
        return await asyncio.wait_for(func(), timeout=timeout_seconds)
    except asyncio.TimeoutError:
        message = timeout_message or f"Operation timed out after {timeout_seconds}s"
        logger.error(message, extra={"timeout": timeout_seconds})
        raise asyncio.TimeoutError(message)


def timeout(seconds: float):
    """
    Decorator for adding timeout to async functions.
    
    Usage:
        @timeout(30.0)
        async def long_running_task():
            ...
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            async def _func():
                return await func(*args, **kwargs)
            
            return await with_timeout(
                _func,
                timeout_seconds=seconds,
                timeout_message=f"{func.__name__} timed out after {seconds}s"
            )
        
        return wrapper
    return decorator
