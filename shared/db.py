from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel
import os
from urllib.parse import urlparse, urlunparse
from typing import Optional
import logging

logger = logging.getLogger(__name__)

# Global engine instance (lazy-loaded)
_engine: Optional[AsyncEngine] = None

def get_engine() -> AsyncEngine:
    """
    Get or create the database engine (lazy initialization).
    This prevents the service from crashing at import time if DATABASE_URL is misconfigured.
    """
    global _engine
    
    if _engine is not None:
        return _engine
    
    # Get DATABASE_URL from environment
    database_url = os.getenv("DATABASE_URL", "").strip()
    
    # Strict validation with actionable error message
    if not database_url:
        error_msg = (
            "DATABASE_URL environment variable is not set.\n"
            "For Railway deployment:\n"
            "  1. Go to Railway dashboard → Your service → Variables tab\n"
            "  2. Add DATABASE_URL with your Supabase connection string\n"
            "  3. Format: postgresql://user:password@host:6543/postgres\n"
            "  4. Redeploy the service"
        )
        logger.error(error_msg)
        raise ValueError(error_msg)
    
    # Parse and sanitize the DATABASE_URL
    try:
        parsed = urlparse(database_url)
        
        # Validate URL structure
        if not parsed.scheme or not parsed.netloc:
            raise ValueError(
                f"Invalid DATABASE_URL format: {database_url}\n"
                f"Expected format: postgresql://user:password@host:port/database"
            )
        
        # Remove query parameters (like ?pgbouncer=true) that SQLAlchemy doesn't need
        sanitized_url = urlunparse((
            parsed.scheme,
            parsed.netloc,
            parsed.path,
            parsed.params,
            '',  # Remove query string
            parsed.fragment
        ))
        
        # Disable statement cache for Supabase Transaction Pooler (Port 6543)
        connect_args = {}
        if "postgresql" in sanitized_url:
            # Ensure we use the asyncpg driver
            if not sanitized_url.startswith("postgresql+asyncpg://"):
                sanitized_url = sanitized_url.replace("postgresql://", "postgresql+asyncpg://")
            connect_args["statement_cache_size"] = 0
        
        logger.info(f"Creating database engine with URL: {parsed.scheme}://{parsed.netloc}{parsed.path}")
        
        _engine = create_async_engine(
            sanitized_url,
            echo=False,
            future=True,
            connect_args=connect_args
        )
        
        return _engine
        
    except Exception as e:
        error_msg = f"Failed to create database engine: {str(e)}\nDATABASE_URL: {database_url}"
        logger.error(error_msg)
        raise ValueError(error_msg) from e

async def init_db():
    """Initialize database tables"""
    engine = get_engine()
    async with engine.begin() as conn:
        # await conn.run_sync(SQLModel.metadata.drop_all)
        await conn.run_sync(SQLModel.metadata.create_all)

async def get_session() -> AsyncSession:
    """Get async database session"""
    engine = get_engine()
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session() as session:
        yield session
