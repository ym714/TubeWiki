import pytest
from worker.services.ai import AIService
from unittest.mock import AsyncMock, MagicMock, patch

@pytest.fixture
def mock_openai():
    with patch("worker.services.ai.AsyncOpenAI") as mock:
        yield mock

@pytest.mark.asyncio
async def test_generate_note_content_success(mock_openai):
    service = AIService()
    mock_client = service.client
    mock_response = MagicMock()
    mock_response.choices[0].message.content = "Generated Note"
    mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
    
    content = await service.generate_note_content("transcript")
    assert content == "Generated Note"
    mock_client.chat.completions.create.assert_called_once()

@pytest.mark.asyncio
async def test_generate_note_content_failure(mock_openai):
    service = AIService()
    service.client.chat.completions.create = AsyncMock(side_effect=Exception("API Error"))
    
    with pytest.raises(Exception):
        await service.generate_note_content("transcript")

@pytest.mark.asyncio
async def test_generate_diagram_success_wrapped(mock_openai):
    service = AIService()
    mock_response = MagicMock()
    mock_response.choices[0].message.content = "```mermaid\ngraph TD\nA-->B\n```"
    service.client.chat.completions.create = AsyncMock(return_value=mock_response)
    
    diagram = await service.generate_diagram("content")
    assert diagram == "graph TD\nA-->B"

@pytest.mark.asyncio
async def test_generate_diagram_success_plain(mock_openai):
    service = AIService()
    mock_response = MagicMock()
    mock_response.choices[0].message.content = "graph TD\nA-->B"
    service.client.chat.completions.create = AsyncMock(return_value=mock_response)
    
    diagram = await service.generate_diagram("content")
    assert diagram == "graph TD\nA-->B"

@pytest.mark.asyncio
async def test_generate_diagram_failure(mock_openai):
    service = AIService()
    service.client.chat.completions.create = AsyncMock(side_effect=Exception("API Error"))
    
    diagram = await service.generate_diagram("content")
    assert diagram == "" # Should return empty string on failure

@pytest.mark.asyncio
async def test_generate_note_content_empty_transcript(mock_openai):
    service = AIService()
    mock_response = MagicMock()
    mock_response.choices[0].message.content = "Empty Note"
    service.client.chat.completions.create = AsyncMock(return_value=mock_response)
    
    content = await service.generate_note_content("")
    assert content == "Empty Note"

@pytest.mark.asyncio
async def test_generate_note_content_long_transcript(mock_openai):
    service = AIService()
    mock_response = MagicMock()
    mock_response.choices[0].message.content = "Note"
    service.client.chat.completions.create = AsyncMock(return_value=mock_response)
    
    long_transcript = "a" * 30000
    await service.generate_note_content(long_transcript)
    
    # Check if truncated
    call_args = service.client.chat.completions.create.call_args[1]
    user_content = call_args["messages"][1]["content"]
    assert len(user_content) < 30000
    assert "Here is the transcript" in user_content

@pytest.mark.asyncio
async def test_generate_diagram_empty_content(mock_openai):
    service = AIService()
    mock_response = MagicMock()
    mock_response.choices[0].message.content = "graph TD"
    service.client.chat.completions.create = AsyncMock(return_value=mock_response)
    
    await service.generate_diagram("")
    service.client.chat.completions.create.assert_called()
