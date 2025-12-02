from pydantic import BaseModel
from typing import Optional, Dict, Any

class JobRequest(BaseModel):
    video_url: str
    user_id: str
    preset: Optional[str] = "default"
    options: Optional[Dict[str, Any]] = {}
