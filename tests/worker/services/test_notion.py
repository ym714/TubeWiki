import pytest
from worker.services.notion import NotionService
from unittest.mock import AsyncMock, patch

@pytest.fixture
def mock_client():
    with patch("worker.services.notion.AsyncClient") as mock:
        yield mock

@pytest.mark.asyncio
async def test_create_page_success(mock_client):
    service = NotionService()
    service.token = "fake_token"
    service.client.pages.create = AsyncMock(return_value={"url": "http://notion.so/page"})
    
    url = await service.create_page("parent_id", "Title", "Content")
    assert url == "http://notion.so/page"
    service.client.pages.create.assert_called_once()

@pytest.mark.asyncio
async def test_create_page_missing_token():
    service = NotionService()
    service.token = None
    
    with pytest.raises(ValueError):
        await service.create_page("parent_id", "Title", "Content")

@pytest.mark.asyncio
async def test_create_page_failure(mock_client):
    service = NotionService()
    service.token = "fake_token"
    service.client.pages.create = AsyncMock(side_effect=Exception("API Error"))
    
    with pytest.raises(Exception):
        await service.create_page("parent_id", "Title", "Content")
