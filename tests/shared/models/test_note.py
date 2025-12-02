import pytest
from datetime import datetime
from shared.models.note import Note, NoteStatus
from pydantic import ValidationError

def test_note_creation_defaults():
    note = Note(user_id="user_1", video_url="http://example.com/video")
    assert note.user_id == "user_1"
    assert note.video_url == "http://example.com/video"
    assert note.status == NoteStatus.PENDING
    assert note.title is None
    assert note.content is None
    assert note.error_message is None
    assert isinstance(note.created_at, datetime)
    assert isinstance(note.updated_at, datetime)

def test_note_creation_full():
    note = Note(
        user_id="user_1",
        video_url="http://example.com/video",
        title="My Video",
        content="Some content",
        status=NoteStatus.COMPLETED,
        error_message="None"
    )
    assert note.title == "My Video"
    assert note.content == "Some content"
    assert note.status == NoteStatus.COMPLETED
    assert note.error_message == "None"

def test_note_status_enum():
    assert NoteStatus.PENDING == "PENDING"
    assert NoteStatus.PROCESSING == "PROCESSING"
    assert NoteStatus.COMPLETED == "COMPLETED"
    assert NoteStatus.FAILED == "FAILED"

def test_note_invalid_status():
    with pytest.raises(ValidationError):
        Note.model_validate({"user_id": "1", "video_url": "url", "status": "INVALID_STATUS"})

def test_note_update_status():
    note = Note(user_id="1", video_url="url")
    note.status = NoteStatus.PROCESSING
    assert note.status == NoteStatus.PROCESSING

def test_note_missing_required_fields():
    with pytest.raises(ValidationError):
        Note.model_validate({"user_id": "1"}) # Missing video_url

def test_note_id_is_none_by_default():
    note = Note(user_id="1", video_url="url")
    assert note.id is None

def test_note_set_id():
    note = Note(user_id="1", video_url="url", id=100)
    assert note.id == 100

def test_note_equality():
    dt = datetime(2023, 1, 1)
    note1 = Note(user_id="1", video_url="url", id=1, created_at=dt, updated_at=dt)
    note2 = Note(user_id="1", video_url="url", id=1, created_at=dt, updated_at=dt)
    assert note1 == note2

def test_note_inequality():
    dt = datetime(2023, 1, 1)
    note1 = Note(user_id="1", video_url="url", id=1, created_at=dt, updated_at=dt)
    note2 = Note(user_id="1", video_url="url", id=2, created_at=dt, updated_at=dt)
    assert note1 != note2

def test_note_repr():
    note = Note(user_id="1", video_url="url")
    assert "user_1" in repr(note) or "user_id='1'" in repr(note)
