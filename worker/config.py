import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    DATABASE_URL = os.getenv("DATABASE_URL")
    QSTASH_CURRENT_SIGNING_KEY = os.getenv("QSTASH_CURRENT_SIGNING_KEY")
    QSTASH_NEXT_SIGNING_KEY = os.getenv("QSTASH_NEXT_SIGNING_KEY")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

    @classmethod
    def validate(cls):
        if not cls.DATABASE_URL:
            raise ValueError("DATABASE_URL is missing")
        if not cls.QSTASH_CURRENT_SIGNING_KEY:
            raise ValueError("QSTASH_CURRENT_SIGNING_KEY is missing")
        if not cls.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is missing")

config = Config()
