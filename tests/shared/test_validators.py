import pytest
from shared.utils.validators import (
    validate_youtube_url,
    validate_email,
    validate_notion_token,
    validate_github_token,
    validate_github_repo,
    sanitize_filename,
    validate_pagination_params
)
from shared.utils.exceptions import InvalidYouTubeURLError, ValidationError

class TestValidators:
    def test_validate_youtube_url_valid(self):
        # Standard URL
        assert validate_youtube_url("https://www.youtube.com/watch?v=dQw4w9WgXcQ") == "dQw4w9WgXcQ"
        # Short URL
        assert validate_youtube_url("https://youtu.be/dQw4w9WgXcQ") == "dQw4w9WgXcQ"
        # Mobile URL
        assert validate_youtube_url("https://m.youtube.com/watch?v=dQw4w9WgXcQ") == "dQw4w9WgXcQ"
        # With extra params
        assert validate_youtube_url("https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=1s") == "dQw4w9WgXcQ"

    def test_validate_youtube_url_invalid(self):
        # Empty
        with pytest.raises(InvalidYouTubeURLError):
            validate_youtube_url("")
        # Invalid domain
        with pytest.raises(InvalidYouTubeURLError):
            validate_youtube_url("https://google.com")
        # No video ID
        with pytest.raises(InvalidYouTubeURLError):
            validate_youtube_url("https://www.youtube.com/watch")
        # Invalid ID format
        with pytest.raises(InvalidYouTubeURLError):
            validate_youtube_url("https://www.youtube.com/watch?v=invalid")

    def test_validate_email(self):
        assert validate_email("test@example.com") is True
        assert validate_email("user.name+tag@domain.co.uk") is True
        assert validate_email("invalid") is False
        assert validate_email("test@") is False
        assert validate_email("@example.com") is False

    def test_validate_notion_token(self):
        assert validate_notion_token("secret_12345678901234567890") is True
        assert validate_notion_token("invalid_token") is False
        assert validate_notion_token("secret_short") is False

    def test_validate_github_token(self):
        assert validate_github_token("ghp_12345678901234567890") is True
        assert validate_github_token("github_pat_12345678901234567890") is True
        assert validate_github_token("invalid") is False

    def test_validate_github_repo(self):
        assert validate_github_repo("owner/repo") is True
        assert validate_github_repo("owner-name/repo-name") is True
        assert validate_github_repo("invalid") is False
        assert validate_github_repo("/repo") is False

    def test_sanitize_filename(self):
        assert sanitize_filename("valid_file.txt") == "valid_file.txt"
        assert sanitize_filename("invalid/file:name?.txt") == "invalidfilename.txt"
        assert sanitize_filename("space name.txt") == "space_name.txt"
        
        # Test max length
        long_name = "a" * 300 + ".txt"
        sanitized = sanitize_filename(long_name, max_length=255)
        assert len(sanitized) <= 255
        assert sanitized.endswith(".txt")

    def test_validate_pagination_params(self):
        assert validate_pagination_params(1, 10) == (1, 10)
        
        with pytest.raises(ValidationError):
            validate_pagination_params(0, 10)
        
        with pytest.raises(ValidationError):
            validate_pagination_params(1, 0)
            
        with pytest.raises(ValidationError):
            validate_pagination_params(1, 101, max_page_size=100)
