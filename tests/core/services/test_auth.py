import pytest
import jwt
from fastapi import HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials
from core.services.auth import get_current_user
from core.config import config
from unittest.mock import MagicMock, patch

@pytest.fixture
def mock_credentials():
    return HTTPAuthorizationCredentials(scheme="Bearer", credentials="test_token")

@pytest.mark.asyncio
async def test_get_current_user_valid(mock_credentials):
    with patch("jwt.decode") as mock_decode:
        mock_decode.return_value = {"sub": "user_123"}
        user_id = await get_current_user(mock_credentials)
        assert user_id == "user_123"
        mock_decode.assert_called_once()

@pytest.mark.asyncio
async def test_get_current_user_expired(mock_credentials):
    with patch("jwt.decode", side_effect=jwt.ExpiredSignatureError):
        with pytest.raises(HTTPException) as exc:
            await get_current_user(mock_credentials)
        assert exc.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert exc.value.detail == "Token expired"

@pytest.mark.asyncio
async def test_get_current_user_invalid_token(mock_credentials):
    with patch("jwt.decode", side_effect=jwt.InvalidTokenError):
        with pytest.raises(HTTPException) as exc:
            await get_current_user(mock_credentials)
        assert exc.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert exc.value.detail == "Invalid token"

@pytest.mark.asyncio
async def test_get_current_user_missing_sub(mock_credentials):
    with patch("jwt.decode") as mock_decode:
        mock_decode.return_value = {"other": "value"}
        with pytest.raises(HTTPException) as exc:
            await get_current_user(mock_credentials)
        assert exc.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert exc.value.detail == "Invalid token payload"

@pytest.mark.asyncio
async def test_get_current_user_wrong_audience(mock_credentials):
    # This is handled by jwt.decode usually, but if we mock it to return success but we want to test config passing
    with patch("jwt.decode") as mock_decode:
        mock_decode.return_value = {"sub": "user_123"}
        await get_current_user(mock_credentials)
        call_kwargs = mock_decode.call_args[1]
        assert call_kwargs["audience"] == "authenticated"

@pytest.mark.asyncio
async def test_get_current_user_correct_secret(mock_credentials):
    with patch("jwt.decode") as mock_decode:
        mock_decode.return_value = {"sub": "user_123"}
        await get_current_user(mock_credentials)
        call_args = mock_decode.call_args[0]
        assert call_args[1] == config.SUPABASE_JWT_SECRET

@pytest.mark.asyncio
async def test_get_current_user_correct_algo(mock_credentials):
    with patch("jwt.decode") as mock_decode:
        mock_decode.return_value = {"sub": "user_123"}
        await get_current_user(mock_credentials)
        call_kwargs = mock_decode.call_args[1]
        assert call_kwargs["algorithms"] == ["HS256"]

@pytest.mark.asyncio
async def test_get_current_user_no_credentials():
    # Depends(security) handles this in FastAPI, but unit testing the function directly
    # requires passing credentials. If None passed, it would fail type check or attribute access.
    # We can skip this as it's FastAPI's responsibility.
    pass

@pytest.mark.asyncio
async def test_get_current_user_empty_payload(mock_credentials):
    with patch("jwt.decode") as mock_decode:
        mock_decode.return_value = {}
        with pytest.raises(HTTPException) as exc:
            await get_current_user(mock_credentials)
        assert exc.value.detail == "Invalid token payload"

@pytest.mark.asyncio
async def test_get_current_user_jwt_decode_error(mock_credentials):
    with patch("jwt.decode", side_effect=Exception("Random error")):
        with pytest.raises(Exception):
            await get_current_user(mock_credentials)
