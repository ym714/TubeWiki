import pytest
from datetime import datetime
from shared.models.user import User
from pydantic import ValidationError

def test_user_creation():
    user = User(id="user_123", email="test@example.com")
    assert user.id == "user_123"
    assert user.email == "test@example.com"
    assert user.is_pro is False
    assert isinstance(user.created_at, datetime)

def test_user_creation_with_pro():
    user = User(id="user_123", email="test@example.com", is_pro=True)
    assert user.is_pro is True

def test_user_default_values():
    user = User(id="user_123", email="test@example.com")
    assert user.is_pro is False
    assert user.created_at is not None

def test_user_invalid_email_type():
    with pytest.raises(ValidationError):
        User.model_validate({"id": "123", "email": 123})

def test_user_missing_id():
    with pytest.raises(ValidationError):
        User.model_validate({"email": "test@example.com"})

def test_user_missing_email():
    with pytest.raises(ValidationError):
        User.model_validate({"id": "123"})

def test_user_update_fields():
    user = User(id="123", email="test@example.com")
    user.email = "new@example.com"
    assert user.email == "new@example.com"

def test_user_repr():
    user = User(id="123", email="test@example.com")
    assert "123" in repr(user)
    assert "test@example.com" in repr(user)

def test_user_equality():
    dt = datetime(2023, 1, 1)
    user1 = User(id="123", email="test@example.com", created_at=dt)
    user2 = User(id="123", email="test@example.com", created_at=dt)
    assert user1 == user2

def test_user_inequality():
    dt = datetime(2023, 1, 1)
    user1 = User(id="123", email="test@example.com", created_at=dt)
    user2 = User(id="124", email="test@example.com", created_at=dt)
    assert user1 != user2

def test_user_with_custom_created_at():
    dt = datetime(2023, 1, 1)
    user = User(id="123", email="test@example.com", created_at=dt)
    assert user.created_at == dt
