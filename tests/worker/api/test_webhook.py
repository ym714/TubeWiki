import pytest
from fastapi.testclient import TestClient
from worker.main import app
from shared.db import get_session
from shared.models.note import Note, NoteStatus
from unittest.mock import AsyncMock, MagicMock, patch
from worker.services.youtube import youtube_service
from worker.services.ai import ai_service
from worker.services.notion import notion_service
from worker.services.security import verify_signature

client = TestClient(app)

@pytest.fixture
def mock_session():
    session = AsyncMock()
    session.commit = AsyncMock()
    session.add = MagicMock()
    session.get = AsyncMock()
    return session

@pytest.fixture
def override_dependencies(mock_session):
    app.dependency_overrides[get_session] = lambda: mock_session
    yield
    app.dependency_overrides = {}

@pytest.mark.asyncio
async def test_process_job_success(override_dependencies, mock_session):
    # Mock services
    with patch("worker.api.webhook.verify_signature"), \
         patch("worker.api.webhook.youtube_service.get_transcript", return_value="transcript"), \
         patch("worker.api.webhook.ai_service.generate_note_content", new_callable=AsyncMock) as mock_ai_content, \
         patch("worker.api.webhook.ai_service.generate_diagram", new_callable=AsyncMock) as mock_ai_diagram, \
         patch("worker.api.webhook.notion_service.create_page", new_callable=AsyncMock) as mock_notion:
        
        mock_ai_content.return_value = "Note Content"
        mock_ai_diagram.return_value = "graph TD"
        mock_notion.return_value = "http://notion.url"
        
        # Mock DB Note
        note = Note(id=1, user_id="u", video_url="url", status=NoteStatus.PENDING)
        mock_session.get.return_value = note
        
        response = client.post(
            "/webhooks/process-job",
            json={"video_url": "url", "user_id": "u", "options": {"note_id": 1, "notion_page_id": "p"}},
            headers={"Upstash-Signature": "sig"}
        )
        
        assert response.status_code == 200
        assert response.json()["status"] == "success"
        assert note.status == NoteStatus.COMPLETED
        assert "Note Content" in note.content
        assert "graph TD" in note.content

@pytest.mark.asyncio
async def test_process_job_missing_signature(override_dependencies):
    response = client.post(
        "/webhooks/process-job",
        json={"video_url": "url", "user_id": "u"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Missing signature"

@pytest.mark.asyncio
async def test_process_job_invalid_signature(override_dependencies):
    with patch("worker.api.webhook.verify_signature", side_effect=Exception("Invalid")):
        response = client.post(
            "/webhooks/process-job",
            json={"video_url": "url", "user_id": "u"},
            headers={"Upstash-Signature": "sig"}
        )
        assert response.status_code == 401

@pytest.mark.asyncio
async def test_process_job_missing_note_id(override_dependencies):
    with patch("worker.api.webhook.verify_signature"):
        response = client.post(
            "/webhooks/process-job",
            json={"video_url": "url", "user_id": "u", "options": {}},
            headers={"Upstash-Signature": "sig"}
        )
        assert response.status_code == 400
        assert response.json()["detail"] == "Missing note_id"

@pytest.mark.asyncio
async def test_process_job_note_not_found(override_dependencies, mock_session):
    with patch("worker.api.webhook.verify_signature"):
        mock_session.get.return_value = None
        
        response = client.post(
            "/webhooks/process-job",
            json={"video_url": "url", "user_id": "u", "options": {"note_id": 1}},
            headers={"Upstash-Signature": "sig"}
        )
        
        assert response.status_code == 200
        assert response.json()["status"] == "skipped"
        assert response.json()["reason"] == "note_not_found"

@pytest.mark.asyncio
async def test_process_job_already_completed(override_dependencies, mock_session):
    with patch("worker.api.webhook.verify_signature"):
        note = Note(id=1, user_id="u", video_url="url", status=NoteStatus.COMPLETED)
        mock_session.get.return_value = note
        
        response = client.post(
            "/webhooks/process-job",
            json={"video_url": "url", "user_id": "u", "options": {"note_id": 1}},
            headers={"Upstash-Signature": "sig"}
        )
        
        assert response.status_code == 200
        assert response.json()["status"] == "skipped"

@pytest.mark.asyncio
async def test_process_job_failure_handling(override_dependencies, mock_session):
    with patch("worker.api.webhook.verify_signature"), \
         patch("worker.api.webhook.youtube_service.get_transcript", side_effect=Exception("YT Error")):
        
        note = Note(id=1, user_id="u", video_url="url", status=NoteStatus.PENDING)
        mock_session.get.return_value = note
        
        response = client.post(
            "/webhooks/process-job",
            json={"video_url": "url", "user_id": "u", "options": {"note_id": 1}},
            headers={"Upstash-Signature": "sig"}
        )
        
        assert response.status_code == 200
        assert response.json()["status"] == "failed"
        assert note.status == NoteStatus.FAILED
        assert "YT Error" in note.error_message

@pytest.mark.asyncio
async def test_process_job_missing_notion_options(override_dependencies, mock_session):
    with patch("worker.api.webhook.verify_signature"), \
         patch("worker.api.webhook.youtube_service.get_transcript", return_value="transcript"), \
         patch("worker.api.webhook.ai_service.generate_note_content", new_callable=AsyncMock) as mock_ai_content, \
         patch("worker.api.webhook.ai_service.generate_diagram", new_callable=AsyncMock) as mock_ai_diagram, \
         patch("worker.api.webhook.notion_service.create_page", new_callable=AsyncMock) as mock_notion:
        
        mock_ai_content.return_value = "Note Content"
        mock_ai_diagram.return_value = ""
        
        note = Note(id=1, user_id="u", video_url="url", status=NoteStatus.PENDING)
        mock_session.get.return_value = note
        
        # Missing notion_page_id
        response = client.post(
            "/webhooks/process-job",
            json={"video_url": "url", "user_id": "u", "options": {"note_id": 1}},
            headers={"Upstash-Signature": "sig"}
        )
        
        assert response.status_code == 200
        assert response.json()["status"] == "success"
        assert response.json()["notion_url"] is None
        mock_notion.assert_not_called()

@pytest.mark.asyncio
async def test_process_job_notion_failure(override_dependencies, mock_session):
    with patch("worker.api.webhook.verify_signature"), \
         patch("worker.api.webhook.youtube_service.get_transcript", return_value="transcript"), \
         patch("worker.api.webhook.ai_service.generate_note_content", new_callable=AsyncMock) as mock_ai_content, \
         patch("worker.api.webhook.ai_service.generate_diagram", new_callable=AsyncMock) as mock_ai_diagram, \
         patch("worker.api.webhook.notion_service.create_page", side_effect=Exception("Notion Error")):
        
        mock_ai_content.return_value = "Note Content"
        mock_ai_diagram.return_value = ""
        
        note = Note(id=1, user_id="u", video_url="url", status=NoteStatus.PENDING)
        mock_session.get.return_value = note
        
        response = client.post(
            "/webhooks/process-job",
            json={"video_url": "url", "user_id": "u", "options": {"note_id": 1, "notion_page_id": "p"}},
            headers={"Upstash-Signature": "sig"}
        )
        
        # Should fail if Notion fails (as per code)
        assert response.status_code == 200
        assert response.json()["status"] == "failed"
        assert note.status == NoteStatus.FAILED

@pytest.mark.asyncio
async def test_process_job_invalid_json_body(override_dependencies):
    with patch("worker.api.webhook.verify_signature"):
        response = client.post(
            "/webhooks/process-job",
            content="invalid json",
            headers={"Upstash-Signature": "sig", "Content-Type": "application/json"}
        )
        assert response.status_code == 400
        assert response.json()["detail"] == "Invalid job format"

@pytest.mark.asyncio
async def test_process_job_signature_verification_called(override_dependencies):
    with patch("worker.api.webhook.verify_signature") as mock_verify:
        client.post(
            "/webhooks/process-job",
            json={"video_url": "url", "user_id": "u"},
            headers={"Upstash-Signature": "sig"}
        )
        mock_verify.assert_called_once()
