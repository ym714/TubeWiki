from fastapi import APIRouter, Request, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from shared.db import get_session
from shared.models.note import Note, NoteStatus
from shared.schemas.job import JobRequest
from worker.services.security import verify_signature
from worker.services.youtube import youtube_service
from worker.services.ai import ai_service
from worker.config import config
import logging
import json

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/webhooks/process-job")
async def process_job(
    request: Request,
    session: AsyncSession = Depends(get_session)
):
    # 1. Verify Signature (skip in local dev)
    body_bytes = await request.body()
    body_str = body_bytes.decode("utf-8")
    signature = request.headers.get("Upstash-Signature")

    # Skip signature verification for local development
    # In production, QStash will always provide a signature
    if signature:
        try:
            verify_signature(body_str, signature)
        except Exception as e:
            logger.error(f"Signature verification failed: {e}")
            raise HTTPException(status_code=401, detail="Invalid signature")
    else:
        logger.warning("No signature provided - assuming local development mode")

    # 2. Parse Job
    try:
        job_data = json.loads(body_str)
        job = JobRequest(**job_data)
    except Exception as e:
        logger.error(f"Failed to parse job: {e}")
        raise HTTPException(status_code=400, detail="Invalid job format")

    note_id = job.options.get("note_id")
    if not note_id:
        logger.error("Missing note_id in job options")
        # Should we fail? Yes.
        raise HTTPException(status_code=400, detail="Missing note_id")

    # 3. Idempotency Check
    note = await session.get(Note, note_id)
    if not note:
        logger.error(f"Note {note_id} not found")
        # If note is gone, we can't process. Return 200 to stop retries? Or 404?
        # If we return 4xx/5xx, QStash retries. If 200, it stops.
        # If note is missing, maybe it was deleted. Stop retries.
        return {"status": "skipped", "reason": "note_not_found"}

    if note.status == NoteStatus.COMPLETED:
        logger.info(f"Note {note_id} already completed. Skipping.")
        return {"status": "skipped", "reason": "already_completed"}

    # 4. Process
    logger.info(f"Processing job for note {note_id}, video {job.video_url}")
    
    # Update status to PROCESSING
    note.status = NoteStatus.PROCESSING
    session.add(note)
    await session.commit()

    try:
        # A. Fetch Transcript
        transcript = await youtube_service.get_transcript(job.video_url)
        
        # B. Generate Content
        content = await ai_service.generate_note_content(transcript)
        
        # C. Generate Diagram
        diagram = await ai_service.generate_diagram(content)
        
        # Append diagram to content
        if diagram:
            content += f"\n\n## Mind Map\n```mermaid\n{diagram}\n```"

        # D. Create Notion Page
        # Simplified Flow: We no longer create Notion pages server-side.
        # The client handles "Copy & Open".
        notion_url = None

        # E. Update Note
        note.content = content # We store markdown in DB too
        note.title = f"Study Guide: {job.video_url}"
        note.status = NoteStatus.COMPLETED
        note.notion_url = notion_url
        
        session.add(note)
        await session.commit()

        logger.info(f"Job completed for note {note_id}")
        return {"status": "success", "note_id": note_id, "notion_url": notion_url}

    except Exception as e:
        logger.error(f"Job failed for note {note_id}: {e}")
        note.status = NoteStatus.FAILED
        note.error_message = str(e)
        session.add(note)
        await session.commit()
        # Raise exception to trigger QStash retry if it's a transient error?
        # If we mark as FAILED in DB, we might not want to retry immediately unless we handle it.
        # For now, let's NOT raise, so QStash stops retrying, assuming it's a permanent error (e.g. invalid video).
        # In a real system, we'd distinguish between transient and permanent errors.
        return {"status": "failed", "reason": str(e)}
