import pytest
import asyncio
import sys
from unittest.mock import MagicMock
import os

# Mock upstash_qstash before any imports
sys.modules["upstash_qstash"] = MagicMock()
sys.modules["upstash_qstash.Receiver"] = MagicMock()

# Set dummy env vars for tests
os.environ["OPENAI_API_KEY"] = "dummy_key"
os.environ["QSTASH_TOKEN"] = "dummy_token"
os.environ["QSTASH_CURRENT_SIGNING_KEY"] = "dummy_key"
os.environ["QSTASH_NEXT_SIGNING_KEY"] = "dummy_key"
os.environ["NOTION_TOKEN"] = "dummy_token"

from typing import AsyncGenerator, Generator
from shared.models.note import Note
# from shared.models.user import User # User model might not be needed for these tests if not used directly

@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel
import pytest_asyncio

# Import app and get_session after setting up mocks
from core.main import app
from shared.db import get_session

@pytest_asyncio.fixture
async def session():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session() as session:
        yield session

@pytest_asyncio.fixture
async def client(session):
    def get_session_override():
        return session
    
    app.dependency_overrides[get_session] = get_session_override
    # Use ASGITransport to avoid deprecation warning or errors with recent httpx
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client
    app.dependency_overrides.clear()

from unittest.mock import AsyncMock

@pytest.fixture(autouse=True)
def mock_qstash(mocker):
    # Mock the qstash_service imported in core.api.notes
    mock = mocker.patch("core.api.notes.qstash_service")
    mock.publish_job = AsyncMock(return_value={"messageId": "msg_123"})
    return mock
