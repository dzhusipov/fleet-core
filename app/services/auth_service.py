from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User, UserRole
from app.repositories.user_repo import UserRepository
from app.utils.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)


class AuthService:
    def __init__(self, session: AsyncSession):
        self.repo = UserRepository(session)
        self.session = session

    async def register(
        self,
        *,
        email: str,
        username: str,
        full_name: str,
        password: str,
        role: UserRole = UserRole.VIEWER,
        language: str = "ru",
    ) -> User:
        """Register a new user."""
        existing = await self.repo.get_by_username(username)
        if existing:
            raise ValueError("Username already taken")

        existing = await self.repo.get_by_email(email)
        if existing:
            raise ValueError("Email already registered")

        user = await self.repo.create(
            email=email,
            username=username,
            full_name=full_name,
            hashed_password=hash_password(password),
            role=role,
            language=language,
        )
        return user

    async def authenticate(self, username: str, password: str) -> tuple[User, str, str]:
        """Authenticate user, return (user, access_token, refresh_token)."""
        user = await self.repo.get_by_username(username)
        if not user or not verify_password(password, user.hashed_password):
            raise ValueError("Invalid username or password")

        if not user.is_active:
            raise ValueError("User account is disabled")

        access_token = create_access_token(user.id, user.role.value)
        refresh_token = create_refresh_token(user.id)
        return user, access_token, refresh_token

    async def refresh_token(self, refresh_token: str) -> tuple[str, str]:
        """Refresh access token."""
        payload = decode_token(refresh_token)
        if not payload or payload.get("type") != "refresh":
            raise ValueError("Invalid refresh token")

        user_id = UUID(payload["sub"])
        user = await self.repo.get_by_id(user_id)
        if not user or not user.is_active:
            raise ValueError("User not found or disabled")

        new_access = create_access_token(user.id, user.role.value)
        new_refresh = create_refresh_token(user.id)
        return new_access, new_refresh

    async def change_password(self, user_id: UUID, current_password: str, new_password: str) -> None:
        """Change user password."""
        user = await self.repo.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")

        if not verify_password(current_password, user.hashed_password):
            raise ValueError("Current password is incorrect")

        await self.repo.update(user, hashed_password=hash_password(new_password))

    async def get_user_by_id(self, user_id: UUID) -> User | None:
        """Get user by ID."""
        return await self.repo.get_by_id(user_id)
