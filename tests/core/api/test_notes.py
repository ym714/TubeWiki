import pytest
from fastapi.testclient import TestClient
from core.main import app
from core.services.auth import get_current_user
from shared.db import get_session
from core.services.qstash import qstash_service
from unittest.mock import AsyncMock, MagicMock

client = TestClient(app)

@pytest.fixture
def mock_session():
    session = AsyncMock()
    session.commit = AsyncMock()
    session.refresh = AsyncMock()
    session.add = MagicMock()
    return session

@pytest.fixture
def override_dependencies(mock_session):
    app.dependency_overrides[get_current_user] = lambda: "user_123"
    app.dependency_overrides[get_session] = lambda: mock_session
    yield
    app.dependency_overrides = {}

@pytest.mark.asyncio
async def test_create_note_success(override_dependencies, mock_session):
    # Mock QStash
    qstash_service.publish_job = AsyncMock(return_value={"messageId": "123"})
    
    response = client.post(
        "/api/v1/notes",
        json={"video_url": "http://example.com", "user_id": "ignored"}
    )
    
    assert response.status_code == 202
    assert response.json()["status"] == "PENDING"
    assert "note_id" in response.json()
    
    # Verify DB interaction
    mock_session.add.assert_called()
    mock_session.commit.assert_called()
    
    # Verify QStash interaction
    qstash_service.publish_job.assert_called_once()

@pytest.mark.asyncio
async def test_create_note_unauthorized():
    # No override for get_current_user
    response = client.post(
        "/api/v1/notes",
        json={"video_url": "http://example.com", "user_id": "ignored"}
    )
    # Since we use HTTPBearer, it returns 403 or 401 depending on implementation details of TestClient/FastAPI default
    # But we haven't mocked the auth dependency, so it will try to run real auth and fail (missing header)
    assert response.status_code == 403 or response.status_code == 401

@pytest.mark.asyncio
async def test_create_note_validation_error(override_dependencies):
    response = client.post(
        "/api/v1/notes",
        json={"user_id": "ignored"} # Missing video_url
    )
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_create_note_qstash_failure(override_dependencies, mock_session):
    # Mock QStash failure
    qstash_service.publish_job = AsyncMock(side_effect=Exception("QStash Error"))
    
    response = client.post(
        "/api/v1/notes",
        json={"video_url": "http://example.com", "user_id": "ignored"}
    )
    
    assert response.status_code == 500
    assert response.json()["detail"] == "Failed to queue job"
    
    # Verify DB rollback/update
    # The code says: new_note.status = NoteStatus.FAILED, then session.add, session.commit
    assert mock_session.commit.call_count == 2 # Once for creation, once for failure update

@pytest.mark.asyncio
async def test_create_note_db_error(override_dependencies, mock_session):
    mock_session.commit.side_effect = Exception("DB Error")
    
    with pytest.raises(Exception):
        client.post(
            "/api/v1/notes",
            json={"video_url": "http://example.com", "user_id": "ignored"}
        )

@pytest.mark.asyncio
async def test_create_note_user_id_override(override_dependencies, mock_session):
    qstash_service.publish_job = AsyncMock(return_value={"messageId": "123"})
    
    client.post(
        "/api/v1/notes",
        json={"video_url": "http://example.com", "user_id": "hacker"}
    )
    
    # Check that the note was created with "user_123" (from override), not "hacker"
    # We need to inspect the call to session.add
    args, _ = mock_session.add.call_args
    note = args[0]
    assert note.user_id == "user_123"

@pytest.mark.asyncio
async def test_create_note_options_passthrough(override_dependencies, mock_session):
    qstash_service.publish_job = AsyncMock(return_value={"messageId": "123"})
    
    client.post(
        "/api/v1/notes",
        json={"video_url": "http://example.com", "user_id": "u", "options": {"lang": "en"}}
    )
    
    args, _ = qstash_service.publish_job.call_args
    job_request = args[0]
    assert job_request.options["lang"] == "en"
    assert "note_id" in job_request.options # Added by the endpoint

@pytest.mark.asyncio
async def test_create_note_preset_default(override_dependencies, mock_session):
    qstash_service.publish_job = AsyncMock(return_value={"messageId": "123"})
    
    client.post(
        "/api/v1/notes",
        json={"video_url": "http://example.com", "user_id": "u"}
    )
    
    args, _ = qstash_service.publish_job.call_args
    job_request = args[0]
    assert job_request.preset == "default"
