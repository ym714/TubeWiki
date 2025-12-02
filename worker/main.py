from fastapi import FastAPI
from worker.api import webhook
from worker.config import config
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="FlashNote AI Worker")

@app.on_event("startup")
async def on_startup():
    try:
        config.validate()
    except Exception as e:
        logger.error(f"Startup failed: {e}")
        # raise e

app.include_router(webhook.router)

@app.get("/healthz")
def health_check():
    return {"status": "ok"}
