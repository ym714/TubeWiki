"""Logging utilities for TubeWiki application."""

import logging
import sys
from typing import Optional
from datetime import datetime


class ColoredFormatter(logging.Formatter):
    """Custom formatter with colors for console output."""
    
    # ANSI color codes
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
        'RESET': '\033[0m'        # Reset
    }
    
    def format(self, record):
        # Add color to level name
        levelname = record.levelname
        if levelname in self.COLORS:
            record.levelname = f"{self.COLORS[levelname]}{levelname}{self.COLORS['RESET']}"
        
        return super().format(record)


def setup_logger(
    name: str,
    level: str = "INFO",
    log_file: Optional[str] = None,
    use_colors: bool = True
) -> logging.Logger:
    """
    Set up a logger with console and optional file handlers.
    
    Args:
        name: Logger name (usually __name__)
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional file path for file logging
        use_colors: Whether to use colored output for console
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))
    
    # Avoid adding handlers multiple times
    if logger.handlers:
        return logger
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, level.upper()))
    
    if use_colors:
        console_format = ColoredFormatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    else:
        console_format = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    
    console_handler.setFormatter(console_format)
    logger.addHandler(console_handler)
    
    # File handler (optional)
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(getattr(logging, level.upper()))
        file_format = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_format)
        logger.addHandler(file_handler)
    
    return logger


def log_request(logger: logging.Logger, method: str, path: str, user_id: Optional[str] = None):
    """Log an incoming HTTP request."""
    user_info = f"user={user_id}" if user_id else "anonymous"
    logger.info(f"Request: {method} {path} ({user_info})")


def log_response(logger: logging.Logger, method: str, path: str, status_code: int, duration_ms: float):
    """Log an HTTP response."""
    logger.info(f"Response: {method} {path} - {status_code} ({duration_ms:.2f}ms)")


def log_error(logger: logging.Logger, error: Exception, context: Optional[dict] = None):
    """Log an error with context."""
    error_type = type(error).__name__
    error_msg = str(error)
    
    context_str = ""
    if context:
        context_str = " | " + " | ".join(f"{k}={v}" for k, v in context.items())
    
    logger.error(f"{error_type}: {error_msg}{context_str}", exc_info=True)


def log_external_api_call(
    logger: logging.Logger,
    service: str,
    operation: str,
    success: bool,
    duration_ms: Optional[float] = None
):
    """Log an external API call."""
    status = "SUCCESS" if success else "FAILED"
    duration_info = f" ({duration_ms:.2f}ms)" if duration_ms else ""
    logger.info(f"External API: {service}.{operation} - {status}{duration_info}")


# Default logger for the application
def get_logger(name: str) -> logging.Logger:
    """Get a logger instance with default configuration."""
    return setup_logger(name, level="INFO", use_colors=True)
