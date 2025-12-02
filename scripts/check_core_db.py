import asyncio
import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

# Load CORE .env
load_dotenv("core/.env")

DATABASE_URL = os.getenv("DATABASE_URL")

async def check_connection():
    if not DATABASE_URL:
        print("DATABASE_URL not found in core/.env")
        return

    # Hide password for log safety
    print(f"Testing connection to: {DATABASE_URL.split('@')[-1]}") 
    
    try:
        # Create engine with the same settings as shared/db.py
        connect_args = {}
        url = DATABASE_URL
        if "postgresql" in url:
            url = url.replace("postgresql://", "postgresql+asyncpg://")
            # Remove pgbouncer param if present, as it might cause issues with asyncpg direct connect
            if "?" in url:
                url = url.split("?")[0]
            connect_args["statement_cache_size"] = 0

        engine = create_async_engine(
            url, 
            echo=False, 
            future=True,
            connect_args=connect_args
        )

        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT 1"))
            print("Connection successful! Result:", result.scalar())
            
    except Exception as e:
        print(f"Connection failed: {e}")
        exit(1)

if __name__ == "__main__":
    asyncio.run(check_connection())
