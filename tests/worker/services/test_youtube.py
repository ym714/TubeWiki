import pytest
from worker.services.youtube import YouTubeService
from unittest.mock import patch, MagicMock

@pytest.fixture
def service():
    return YouTubeService()

def test_extract_video_id_standard(service):
    url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    assert service.extract_video_id(url) == "dQw4w9WgXcQ"

def test_extract_video_id_short(service):
    url = "https://youtu.be/dQw4w9WgXcQ"
    assert service.extract_video_id(url) == "dQw4w9WgXcQ"

def test_extract_video_id_embed(service):
    url = "https://www.youtube.com/embed/dQw4w9WgXcQ"
    assert service.extract_video_id(url) == "dQw4w9WgXcQ"

def test_extract_video_id_v(service):
    url = "https://www.youtube.com/v/dQw4w9WgXcQ"
    assert service.extract_video_id(url) == "dQw4w9WgXcQ"

def test_extract_video_id_invalid(service):
    with pytest.raises(ValueError):
        service.extract_video_id("https://example.com/video")

def test_get_transcript_success(service):
    with patch("worker.services.youtube.YouTubeTranscriptApi") as mock_api:
        mock_api.get_transcript.return_value = [{"text": "Hello"}, {"text": "World"}]
        transcript = service.get_transcript("https://youtu.be/123")
        assert transcript == "Hello World"
        mock_api.get_transcript.assert_called_with("123", languages=['ja', 'en'])

def test_get_transcript_failure(service):
    with patch("worker.services.youtube.YouTubeTranscriptApi") as mock_api:
        mock_api.get_transcript.side_effect = Exception("No transcript")
        with pytest.raises(Exception):
            service.get_transcript("https://youtu.be/123")
