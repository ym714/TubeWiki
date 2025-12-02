from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

class User(SQLModel, table=True):
    __tablename__ = "users"

    id: str = Field(primary_key=True)  # Supabase Auth ID
    email: str = Field(index=True, unique=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    is_pro: bool = Field(default=False)
