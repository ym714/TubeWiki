import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    DATABASE_URL = os.getenv("DATABASE_URL")
    QSTASH_URL = os.getenv("QSTASH_URL", "https://qstash.upstash.io/v1/publish")
    QSTASH_TOKEN = os.getenv("QSTASH_TOKEN")
    WORKER_URL = os.getenv("WORKER_URL")
    SUPABASE_JWT_SECRET = os.getenv("SUPABASE_JWT_SECRET")

    @classmethod
    def validate(cls):
        if not cls.DATABASE_URL:
            raise ValueError("DATABASE_URL is missing")
        if not cls.QSTASH_TOKEN:
            raise ValueError("QSTASH_TOKEN is missing")
        if not cls.WORKER_URL:
            raise ValueError("WORKER_URL is missing")
        if not cls.SUPABASE_JWT_SECRET:
            raise ValueError("SUPABASE_JWT_SECRET is missing")
        if not cls.STRIPE_SECRET_KEY:
            raise ValueError("STRIPE_SECRET_KEY is missing")
        if not cls.STRIPE_PRICE_ID:
            raise ValueError("STRIPE_PRICE_ID is missing")

    STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")
    STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")
    STRIPE_PRICE_ID = os.getenv("STRIPE_PRICE_ID")

config = Config()
