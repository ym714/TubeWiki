from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from shared.db import get_session
from shared.models.note import Note, NoteStatus
from shared.schemas.job import JobRequest
from core.services.qstash import qstash_service
from core.services.auth import get_current_user
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/notes", status_code=status.HTTP_202_ACCEPTED)
async def create_note(
    request: JobRequest,
    session: AsyncSession = Depends(get_session),
    user_id: str = Depends(get_current_user)
):
    # Override user_id from token to ensure security
    request.user_id = user_id

    # 1. Create Note in DB
    new_note = Note(
        user_id=request.user_id,
        video_url=request.video_url,
        status=NoteStatus.PENDING
    )
    session.add(new_note)
    await session.commit()
    await session.refresh(new_note)

    # 2. Publish to QStash
    try:
        # We might want to pass the note_id to the worker
        request.options["note_id"] = new_note.id
        await qstash_service.publish_job(request)
    except Exception as e:
        # If QStash fails, we might want to mark note as FAILED or delete it
        # For now, just log and return error (or keep it pending for retry?)
        # Since we return 202, we should probably rollback or mark failed.
        logger.error(f"Failed to publish job: {e}")
        new_note.status = NoteStatus.FAILED
        new_note.error_message = str(e)
        session.add(new_note)
        await session.commit()
        raise HTTPException(status_code=500, detail="Failed to queue job")

    return {"message": "Job accepted", "note_id": new_note.id, "status": "PENDING"}

@router.get("/notes/{note_id}", response_model=Note)
async def get_note(
    note_id: int,
    session: AsyncSession = Depends(get_session),
    user_id: str = Depends(get_current_user)
):
    note = await session.get(Note, note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    
    # Ensure user owns the note
    if note.user_id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to access this note")
        
    return note

@router.get("/notes/by-url/", response_model=Note)
async def get_note_by_url(
    video_url: str,
    session: AsyncSession = Depends(get_session),
    user_id: str = Depends(get_current_user)
):
    from sqlmodel import select
    statement = select(Note).where(Note.video_url == video_url, Note.user_id == user_id)
    results = await session.exec(statement)
    note = results.first()
    
    if not note:
        raise HTTPException(status_code=404, detail="Note not found for this video")
        
    return note
