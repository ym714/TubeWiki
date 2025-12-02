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

@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()
