from pydantic import BaseModel, validator
from typing import Optional, Dict, Any
from shared.utils.validators import validate_youtube_url

class JobRequest(BaseModel):
    video_url: str
    user_id: str
    preset: Optional[str] = "default"
    options: Optional[Dict[str, Any]] = {}

    @validator("video_url")
    def validate_url(cls, v):
        validate_youtube_url(v)
        return v
