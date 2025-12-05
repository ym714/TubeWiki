from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel
import os

# Use shared config or os.getenv directly to avoid circular imports if config is in core
DATABASE_URL = os.getenv("DATABASE_URL")

# Strict validation: DATABASE_URL is required in production
if not DATABASE_URL:
    raise ValueError(
        "DATABASE_URL environment variable is not set. "
        "Please configure it in Railway settings or your .env file."
    )

# Disable statement cache for Supabase Transaction Pooler (Port 6543)
connect_args = {}
if "postgresql" in DATABASE_URL:
    # Ensure we use the asyncpg driver
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")
    connect_args["statement_cache_size"] = 0

engine = create_async_engine(
    DATABASE_URL, 
    echo=False, 
    future=True,
    connect_args=connect_args
)

async def init_db():
    async with engine.begin() as conn:
        # await conn.run_sync(SQLModel.metadata.drop_all)
        await conn.run_sync(SQLModel.metadata.create_all)

async def get_session() -> AsyncSession:
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session() as session:
        yield session
