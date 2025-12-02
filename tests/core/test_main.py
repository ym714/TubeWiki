import pytest
from fastapi.testclient import TestClient
from core.main import app
from unittest.mock import patch, AsyncMock

client = TestClient(app)

def test_health_check():
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

@pytest.mark.asyncio
async def test_startup_success():
    with patch("core.config.config.validate") as mock_validate, \
         patch("core.main.init_db", new_callable=AsyncMock) as mock_init_db:
        
        # Manually trigger startup
        await app.router.startup()
        
        mock_validate.assert_called()
        mock_init_db.assert_called()

@pytest.mark.asyncio
async def test_startup_failure_db():
    with patch("core.config.config.validate"), \
         patch("core.main.init_db", side_effect=Exception("DB Init Failed")) as mock_init_db, \
         patch("core.main.logger.error") as mock_log:
        
        # Manually trigger startup
        await app.router.startup()
            
        mock_log.assert_called()
        assert "Startup failed" in mock_log.call_args[0][0]

@pytest.mark.asyncio
async def test_startup_failure_config():
    with patch("core.config.config.validate", side_effect=Exception("Config Invalid")), \
         patch("core.main.logger.error") as mock_log:
        
        with TestClient(app) as c:
            pass
            
        mock_log.assert_called()

def test_api_router_included():
    # Check if /api/v1/notes is in routes
    routes = [route.path for route in app.routes]
    assert "/api/v1/notes" in routes
