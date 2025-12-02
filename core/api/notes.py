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
