import pytest
from core.services.qstash import QStashService
from shared.schemas.job import JobRequest
from unittest.mock import MagicMock, AsyncMock
import httpx

@pytest.fixture
def job_request():
    return JobRequest(video_url="http://example.com", user_id="user_1")

@pytest.mark.asyncio
async def test_publish_job_success(job_request):
    service = QStashService()
    service.client.post = AsyncMock(return_value=MagicMock(status_code=200, json=lambda: {"messageId": "msg_123"}))
    
    response = await service.publish_job(job_request)
    assert response["messageId"] == "msg_123"
    service.client.post.assert_called_once()

@pytest.mark.asyncio
async def test_publish_job_failure_500(job_request):
    service = QStashService()
    mock_response = MagicMock(status_code=500)
    mock_response.raise_for_status.side_effect = httpx.HTTPStatusError("Error", request=None, response=mock_response)
    service.client.post = AsyncMock(return_value=mock_response)
    
    with pytest.raises(httpx.HTTPStatusError):
        await service.publish_job(job_request)

@pytest.mark.asyncio
async def test_publish_job_network_error(job_request):
    service = QStashService()
    service.client.post = AsyncMock(side_effect=httpx.NetworkError("Network error"))
    
    with pytest.raises(httpx.NetworkError):
        await service.publish_job(job_request)

@pytest.mark.asyncio
async def test_publish_job_correct_headers(job_request):
    service = QStashService()
    service.client.post = AsyncMock(return_value=MagicMock(status_code=200, json=lambda: {}))
    
    await service.publish_job(job_request)
    call_kwargs = service.client.post.call_args[1]
    assert call_kwargs["headers"]["Content-Type"] == "application/json"
    assert call_kwargs["headers"]["Upstash-Retries"] == "3"

@pytest.mark.asyncio
async def test_publish_job_correct_payload(job_request):
    service = QStashService()
    service.client.post = AsyncMock(return_value=MagicMock(status_code=200, json=lambda: {}))
    
    await service.publish_job(job_request)
    call_kwargs = service.client.post.call_args[1]
    assert call_kwargs["json"] == job_request.dict()

@pytest.mark.asyncio
async def test_publish_job_exception_logging(job_request, caplog):
    service = QStashService()
    service.client.post = AsyncMock(side_effect=Exception("Unexpected error"))
    
    with pytest.raises(Exception):
        await service.publish_job(job_request)
    
    assert "Failed to publish job to QStash" in caplog.text
