from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field
from enum import Enum

class NoteStatus(str, Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

class Note(SQLModel, table=True):
    __tablename__ = "notes"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True)
    video_url: str = Field(index=True)
    title: Optional[str] = None
    content: Optional[str] = None  # Notion Page ID or Markdown content
    status: NoteStatus = Field(default=NoteStatus.PENDING)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    error_message: Optional[str] = None
