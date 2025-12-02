from fastapi import FastAPI
from core.api import notes
from core.config import config
from shared.db import init_db
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="FlashNote AI Core")

@app.on_event("startup")
async def on_startup():
    try:
        config.validate()
        # In production with Vercel, we might not run init_db() here if it's serverless
        # But for Cloud Run or local, it's fine.
        # For Vercel, usually we run migrations separately.
        # We'll keep it for now but wrap in try/except or check env.
        await init_db()
    except Exception as e:
        logger.error(f"Startup failed: {e}")
        # raise e # Don't crash if just DB init fails (e.g. connection issues)

app.include_router(notes.router, prefix="/api/v1")

@app.get("/healthz")
def health_check():
    return {"status": "ok"}
