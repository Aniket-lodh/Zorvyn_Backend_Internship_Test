import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field

from app.models.user import UserRole


class UserCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100, examples=["Alice Johnson"])
    email: EmailStr = Field(examples=["alice@example.com"])
    role: UserRole = Field(default=UserRole.VIEWER, examples=["admin"])


class UserUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    email: EmailStr | None = Field(default=None)
    role: UserRole | None = Field(default=None)
    is_active: bool | None = Field(default=None)


class UserResponse(BaseModel):
    id: uuid.UUID
    name: str
    email: str
    role: UserRole
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
