import httpx
from core.config import config
from shared.schemas.job import JobRequest
import logging

logger = logging.getLogger(__name__)

class QStashService:
    def __init__(self):
        self.client = httpx.AsyncClient(
            headers={"Authorization": f"Bearer {config.QSTASH_TOKEN}"}
        )

    async def publish_job(self, job: JobRequest):
        url = f"{config.QSTASH_URL}/{config.WORKER_URL}"
        
        try:
            response = await self.client.post(
                url,
                json=job.dict(),
                headers={
                    "Content-Type": "application/json",
                    "Upstash-Retries": "3"
                }
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to publish job to QStash: {e}")
            raise

qstash_service = QStashService()
