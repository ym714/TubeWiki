"""Validation utilities for TubeWiki application."""

import re
from typing import Optional
from urllib.parse import urlparse, parse_qs

from shared.utils.exceptions import InvalidYouTubeURLError, ValidationError


def validate_youtube_url(url: str) -> str:
    """
    Validate and extract video ID from YouTube URL.
    
    Args:
        url: YouTube URL to validate
        
    Returns:
        Video ID if valid
        
    Raises:
        InvalidYouTubeURLError: If URL is invalid
    """
    if not url:
        raise InvalidYouTubeURLError("", details={"reason": "URL is empty"})
    
    # Parse URL
    try:
        parsed = urlparse(url)
    except Exception as e:
        raise InvalidYouTubeURLError(url, details={"reason": str(e)})
    
    # Check domain
    valid_domains = ['youtube.com', 'www.youtube.com', 'youtu.be', 'm.youtube.com']
    if parsed.netloc not in valid_domains:
        raise InvalidYouTubeURLError(url, details={"reason": "Invalid domain"})
    
    # Extract video ID
    video_id = None
    
    # Format: https://www.youtube.com/watch?v=VIDEO_ID
    if parsed.netloc in ['youtube.com', 'www.youtube.com', 'm.youtube.com']:
        if parsed.path == '/watch':
            query_params = parse_qs(parsed.query)
            video_id = query_params.get('v', [None])[0]
    
    # Format: https://youtu.be/VIDEO_ID
    elif parsed.netloc == 'youtu.be':
        video_id = parsed.path.lstrip('/')
    
    if not video_id:
        raise InvalidYouTubeURLError(url, details={"reason": "Could not extract video ID"})
    
    # Validate video ID format (11 characters, alphanumeric + - and _)
    if not re.match(r'^[a-zA-Z0-9_-]{11}$', video_id):
        raise InvalidYouTubeURLError(url, details={"reason": "Invalid video ID format"})
    
    return video_id


def validate_email(email: str) -> bool:
    """
    Validate email format.
    
    Args:
        email: Email address to validate
        
    Returns:
        True if valid, False otherwise
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_notion_token(token: str) -> bool:
    """
    Validate Notion integration token format.
    
    Args:
        token: Notion token to validate
        
    Returns:
        True if valid format
    """
    # Notion tokens start with "secret_"
    return token.startswith("secret_") and len(token) > 20


def validate_github_token(token: str) -> bool:
    """
    Validate GitHub personal access token format.
    
    Args:
        token: GitHub token to validate
        
    Returns:
        True if valid format
    """
    # GitHub classic tokens start with "ghp_"
    # GitHub fine-grained tokens start with "github_pat_"
    return (token.startswith("ghp_") or token.startswith("github_pat_")) and len(token) > 20


def validate_github_repo(repo: str) -> bool:
    """
    Validate GitHub repository format (owner/repo).
    
    Args:
        repo: Repository string to validate
        
    Returns:
        True if valid format
    """
    pattern = r'^[a-zA-Z0-9_-]+/[a-zA-Z0-9_-]+$'
    return bool(re.match(pattern, repo))


def sanitize_filename(filename: str, max_length: int = 255) -> str:
    """
    Sanitize filename by removing invalid characters.
    
    Args:
        filename: Original filename
        max_length: Maximum length for filename
        
    Returns:
        Sanitized filename
    """
    # Remove invalid characters
    sanitized = re.sub(r'[<>:"/\\|?*]', '', filename)
    
    # Replace spaces with underscores
    sanitized = sanitized.replace(' ', '_')
    
    # Limit length
    if len(sanitized) > max_length:
        name, ext = sanitized.rsplit('.', 1) if '.' in sanitized else (sanitized, '')
        name = name[:max_length - len(ext) - 1]
        sanitized = f"{name}.{ext}" if ext else name
    
    return sanitized


def validate_note_status(status: str) -> bool:
    """
    Validate note status value.
    
    Args:
        status: Status to validate
        
    Returns:
        True if valid status
    """
    valid_statuses = ['PENDING', 'PROCESSING', 'COMPLETED', 'FAILED']
    return status in valid_statuses


def validate_pagination_params(page: int, page_size: int, max_page_size: int = 100) -> tuple[int, int]:
    """
    Validate and normalize pagination parameters.
    
    Args:
        page: Page number (1-indexed)
        page_size: Number of items per page
        max_page_size: Maximum allowed page size
        
    Returns:
        Tuple of (validated_page, validated_page_size)
        
    Raises:
        ValidationError: If parameters are invalid
    """
    if page < 1:
        raise ValidationError("Page number must be >= 1")
    
    if page_size < 1:
        raise ValidationError("Page size must be >= 1")
    
    if page_size > max_page_size:
        raise ValidationError(f"Page size must be <= {max_page_size}")
    
    return page, page_size
