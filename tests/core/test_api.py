import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from shared.models.note import Note, NoteStatus
from core.main import app
from core.services.auth import get_current_user

@pytest.mark.asyncio
async def test_health_check(client: AsyncClient):
    response = await client.get("/healthz")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

@pytest.mark.asyncio
async def test_create_note(client: AsyncClient, session: AsyncSession):
    # Override auth
    app.dependency_overrides[get_current_user] = lambda: "test_user_id"
    
    try:
        # Test creating a new note
        response = await client.post(
            "/api/v1/notes",
            json={"video_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ", "user_id": "test_user_id"}
        )
        assert response.status_code == 202
        data = response.json()
        assert data["status"] == "PENDING"
        assert "note_id" in data
        
        # Verify DB
        note = await session.get(Note, data["note_id"])
        assert note is not None
        assert note.video_url == "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        assert note.user_id == "test_user_id"
    finally:
        app.dependency_overrides.pop(get_current_user, None)

@pytest.mark.asyncio
async def test_create_note_invalid_url(client: AsyncClient):
    app.dependency_overrides[get_current_user] = lambda: "test_user_id"
    try:
        response = await client.post(
            "/api/v1/notes",
            json={"video_url": "invalid-url", "user_id": "test_user_id"}
        )
        assert response.status_code == 422 # Validation error
    finally:
        app.dependency_overrides.pop(get_current_user, None)

@pytest.mark.asyncio
async def test_get_note(client: AsyncClient, session: AsyncSession):
    app.dependency_overrides[get_current_user] = lambda: "test_user_id"
    try:
        # Create a note directly in DB
        note = Note(
            user_id="test_user_id",
            video_url="https://www.youtube.com/watch?v=test",
            title="Test Video",
            content="Test Content",
            status=NoteStatus.COMPLETED
        )
        session.add(note)
        await session.commit()
        await session.refresh(note)
        
        # Get note by ID
        response = await client.get(f"/api/v1/notes/{note.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Test Video"
        assert data["content"] == "Test Content"
        assert data["status"] == "COMPLETED"
    finally:
        app.dependency_overrides.pop(get_current_user, None)

@pytest.mark.asyncio
async def test_get_note_not_found(client: AsyncClient):
    app.dependency_overrides[get_current_user] = lambda: "test_user_id"
    try:
        response = await client.get("/api/v1/notes/99999")
        assert response.status_code == 404
    finally:
        app.dependency_overrides.pop(get_current_user, None)
