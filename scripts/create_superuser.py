"""Create a superuser (admin) account."""

import asyncio
import sys

from app.database import AsyncSessionLocal
from app.models.user import UserRole
from app.services.auth_service import AuthService


async def main():
    username = input("Username [admin]: ").strip() or "admin"
    email = input("Email [admin@fleetcore.local]: ").strip() or "admin@fleetcore.local"
    full_name = input("Full name [Administrator]: ").strip() or "Administrator"
    password = input("Password [admin123]: ").strip() or "admin123"

    async with AsyncSessionLocal() as session:
        service = AuthService(session)
        try:
            user = await service.register(
                email=email,
                username=username,
                full_name=full_name,
                password=password,
                role=UserRole.ADMIN,
            )
            await session.commit()
            print(f"Superuser created: {user.username} ({user.email})")
        except ValueError as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
