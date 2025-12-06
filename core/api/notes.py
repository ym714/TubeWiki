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
):
    # Use anonymous user_id
    if not request.user_id:
        request.user_id = "anonymous"

    # 1. Create Note in DB
    new_note = Note(
        user_id=request.user_id,
        video_url=request.video_url,
        status=NoteStatus.PENDING
    )
    session.add(new_note)
    await session.commit()
    await session.refresh(new_note)

    # 2. Publish to QStash or Call Worker Directly
    try:
        # We might want to pass the note_id to the worker
        request.options["note_id"] = new_note.id
        
        import os
        import httpx
        
        worker_url = os.getenv("WORKER_URL", "http://localhost:8001")
        
        # If running locally (localhost) or internal Railway network, bypass QStash and call worker directly
        if "localhost" in worker_url or "127.0.0.1" in worker_url or "railway.internal" in worker_url:
            logger.info(f"Running locally, bypassing QStash. Calling worker at {worker_url}")
            async with httpx.AsyncClient() as client:
                # The worker endpoint expects the same payload
                response = await client.post(
                    f"{worker_url}/webhooks/process-job",
                    json=request.dict(),
                    timeout=120.0  # Increased timeout for AI generation
                )
                if response.status_code >= 400:
                    raise Exception(f"Worker returned {response.status_code}: {response.text}")
        else:
            # Production: Use QStash
            await qstash_service.publish_job(request)
            
    except Exception as e:
        # If QStash/Worker fails, we might want to mark note as FAILED or delete it
        # For now, just log and return error (or keep it pending for retry?)
        # Since we return 202, we should probably rollback or mark failed.
        logger.error(f"Failed to publish job: {e}")
        new_note.status = NoteStatus.FAILED
        new_note.error_message = str(e)
        session.add(new_note)
        await session.commit()
        raise HTTPException(status_code=500, detail=f"Failed to queue job: {str(e)}")

    return {"message": "Job accepted", "note_id": new_note.id, "status": "PENDING"}

@router.get("/notes/{note_id}", response_model=Note)
async def get_note(
    note_id: int,
    session: AsyncSession = Depends(get_session),
):
    user_id = "anonymous"
    note = await session.get(Note, note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    
    # Ensure user owns the note
    if note.user_id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to access this note")
        
    logger.info(f"Returning note {note_id}. Content length: {len(note.content) if note.content else 0}")
    return note

@router.get("/notes/by-url/", response_model=Note)
async def get_note_by_url(
    video_url: str,
    session: AsyncSession = Depends(get_session),
):
    user_id = "anonymous"
    from sqlmodel import select
    statement = select(Note).where(Note.video_url == video_url, Note.user_id == user_id)
    results = await session.exec(statement)
    note = results.first()
    
    if not note:
        raise HTTPException(status_code=404, detail="Note not found for this video")
        
    return note
