from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field

from app.models.user import UserRole


class UserCreate(BaseModel):
    email: str = Field(..., max_length=255)
    username: str = Field(..., min_length=3, max_length=100)
    full_name: str = Field(..., min_length=1, max_length=255)
    password: str = Field(..., min_length=6, max_length=128)
    role: UserRole = UserRole.VIEWER
    language: str = Field("ru", max_length=5)


class UserUpdate(BaseModel):
    email: str | None = Field(None, max_length=255)
    full_name: str | None = Field(None, max_length=255)
    role: UserRole | None = None
    is_active: bool | None = None
    language: str | None = Field(None, max_length=5)


class UserRead(BaseModel):
    id: UUID
    email: str
    username: str
    full_name: str
    role: UserRole
    is_active: bool
    language: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str


class PasswordChange(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=6, max_length=128)
