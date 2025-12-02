"""Custom exceptions for TubeWiki application."""

from typing import Optional


class TubeWikiException(Exception):
    """Base exception for all TubeWiki errors."""
    
    def __init__(self, message: str, status_code: int = 500, details: Optional[dict] = None):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


# Authentication & Authorization Errors
class AuthenticationError(TubeWikiException):
    """Raised when authentication fails."""
    
    def __init__(self, message: str = "Authentication failed", details: Optional[dict] = None):
        super().__init__(message, status_code=401, details=details)


class AuthorizationError(TubeWikiException):
    """Raised when user is not authorized."""
    
    def __init__(self, message: str = "Not authorized", details: Optional[dict] = None):
        super().__init__(message, status_code=403, details=details)


# Resource Errors
class ResourceNotFoundError(TubeWikiException):
    """Raised when a requested resource is not found."""
    
    def __init__(self, resource: str, resource_id: str, details: Optional[dict] = None):
        message = f"{resource} with id '{resource_id}' not found"
        super().__init__(message, status_code=404, details=details)


class ResourceAlreadyExistsError(TubeWikiException):
    """Raised when trying to create a resource that already exists."""
    
    def __init__(self, resource: str, details: Optional[dict] = None):
        message = f"{resource} already exists"
        super().__init__(message, status_code=409, details=details)


# Validation Errors
class ValidationError(TubeWikiException):
    """Raised when input validation fails."""
    
    def __init__(self, message: str = "Validation failed", details: Optional[dict] = None):
        super().__init__(message, status_code=422, details=details)


class InvalidYouTubeURLError(ValidationError):
    """Raised when YouTube URL is invalid."""
    
    def __init__(self, url: str, details: Optional[dict] = None):
        message = f"Invalid YouTube URL: {url}"
        super().__init__(message, details=details)


# External Service Errors
class ExternalServiceError(TubeWikiException):
    """Raised when an external service fails."""
    
    def __init__(self, service: str, message: str, details: Optional[dict] = None):
        full_message = f"{service} error: {message}"
        super().__init__(full_message, status_code=502, details=details)


class YouTubeAPIError(ExternalServiceError):
    """Raised when YouTube API fails."""
    
    def __init__(self, message: str, details: Optional[dict] = None):
        super().__init__("YouTube API", message, details)


class GroqAPIError(ExternalServiceError):
    """Raised when Groq API fails."""
    
    def __init__(self, message: str, details: Optional[dict] = None):
        super().__init__("Groq API", message, details)


class NotionAPIError(ExternalServiceError):
    """Raised when Notion API fails."""
    
    def __init__(self, message: str, details: Optional[dict] = None):
        super().__init__("Notion API", message, details)


class QStashError(ExternalServiceError):
    """Raised when QStash fails."""
    
    def __init__(self, message: str, details: Optional[dict] = None):
        super().__init__("QStash", message, details)


# Processing Errors
class ProcessingError(TubeWikiException):
    """Raised when note processing fails."""
    
    def __init__(self, message: str = "Processing failed", details: Optional[dict] = None):
        super().__init__(message, status_code=500, details=details)


class TranscriptNotAvailableError(ProcessingError):
    """Raised when video transcript is not available."""
    
    def __init__(self, video_id: str, details: Optional[dict] = None):
        message = f"Transcript not available for video: {video_id}"
        super().__init__(message, details=details)


class AIGenerationError(ProcessingError):
    """Raised when AI generation fails."""
    
    def __init__(self, message: str = "AI generation failed", details: Optional[dict] = None):
        super().__init__(message, details=details)


# Rate Limiting
class RateLimitExceededError(TubeWikiException):
    """Raised when rate limit is exceeded."""
    
    def __init__(self, message: str = "Rate limit exceeded", retry_after: Optional[int] = None):
        details = {"retry_after": retry_after} if retry_after else {}
        super().__init__(message, status_code=429, details=details)


# Payment Errors
class PaymentError(TubeWikiException):
    """Raised when payment processing fails."""
    
    def __init__(self, message: str = "Payment failed", details: Optional[dict] = None):
        super().__init__(message, status_code=402, details=details)


class SubscriptionRequiredError(TubeWikiException):
    """Raised when a pro subscription is required."""
    
    def __init__(self, message: str = "Pro subscription required", details: Optional[dict] = None):
        super().__init__(message, status_code=403, details=details)
