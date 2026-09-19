from datetime import datetime

from beanie import Document
from pydantic import EmailStr, Field
from pymongo import IndexModel


class User(Document):
    name: str = Field(..., min_length=3, max_length=15)
    email: EmailStr
    password_hash: str
    role: str = "user"
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "users"
        indexes = [
            IndexModel("email", unique=True),
        ]