import os
from dotenv import load_dotenv

from pathlib import Path
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)

class Config:
    DATABASE_URL = os.getenv("DATABASE_URL")
    QSTASH_CURRENT_SIGNING_KEY = os.getenv("QSTASH_CURRENT_SIGNING_KEY")
    QSTASH_NEXT_SIGNING_KEY = os.getenv("QSTASH_NEXT_SIGNING_KEY")
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    NOTION_TOKEN = os.getenv("NOTION_TOKEN")

    @classmethod
    def validate(cls):
        if not cls.DATABASE_URL:
            raise ValueError("DATABASE_URL is missing")
        if not cls.QSTASH_CURRENT_SIGNING_KEY:
            raise ValueError("QSTASH_CURRENT_SIGNING_KEY is missing")
        if not cls.GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY is missing")

config = Config()
