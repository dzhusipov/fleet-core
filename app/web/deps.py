from uuid import UUID

from fastapi import Depends, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User, UserRole
from app.repositories.user_repo import UserRepository


async def get_web_user(request: Request, db: AsyncSession = Depends(get_db)) -> User | None:
    """Get current user from session cookie. Returns None if not authenticated."""
    user_id = request.session.get("user_id")
    if not user_id:
        return None
    repo = UserRepository(db)
    user = await repo.get_by_id(UUID(user_id))
    if not user or not user.is_active:
        request.session.clear()
        return None
    return user


async def require_web_user(request: Request, db: AsyncSession = Depends(get_db)) -> User:
    """Require authenticated user, redirect to login if not."""
    user = await get_web_user(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=302)
    return user


def web_require_roles(*roles: UserRole):
    """Dependency factory for web routes requiring specific roles."""

    async def check_role(request: Request, db: AsyncSession = Depends(get_db)) -> User:
        user = await get_web_user(request, db)
        if not user:
            return RedirectResponse(url="/login", status_code=302)
        if user.role not in roles:
            return RedirectResponse(url="/", status_code=302)
        return user

    return check_role
