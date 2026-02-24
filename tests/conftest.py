"""Test fixtures for FleetCore."""

from uuid import uuid4

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from app.config import settings
from app.database import get_db
from app.main import create_app
from app.models.user import User, UserRole
from app.utils.security import create_access_token, hash_password

TEST_DATABASE_URL = settings.DATABASE_URL


@pytest_asyncio.fixture
async def db_session():
    """Create a test DB session with transaction rollback."""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    connection = await engine.connect()
    transaction = await connection.begin()
    session = AsyncSession(bind=connection, expire_on_commit=False)

    yield session

    await session.close()
    await transaction.rollback()
    await connection.close()
    await engine.dispose()


@pytest_asyncio.fixture
async def app(db_session):
    """Create a test FastAPI app with overridden DB dependency."""
    application = create_app()

    async def override_get_db():
        yield db_session

    application.dependency_overrides[get_db] = override_get_db
    return application


@pytest_asyncio.fixture
async def client(app):
    """Create an async HTTP test client."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac


@pytest_asyncio.fixture
async def admin_user(db_session: AsyncSession) -> User:
    """Create an admin user for testing."""
    user = User(
        id=uuid4(),
        email="testadmin@test.com",
        username="testadmin",
        full_name="Test Admin",
        hashed_password=hash_password("testpass123"),
        role=UserRole.ADMIN,
        is_active=True,
        language="en",
    )
    db_session.add(user)
    await db_session.flush()
    return user


@pytest_asyncio.fixture
async def fleet_manager_user(db_session: AsyncSession) -> User:
    """Create a fleet manager user for testing."""
    user = User(
        id=uuid4(),
        email="testmanager@test.com",
        username="testmanager",
        full_name="Test Manager",
        hashed_password=hash_password("testpass123"),
        role=UserRole.FLEET_MANAGER,
        is_active=True,
        language="en",
    )
    db_session.add(user)
    await db_session.flush()
    return user


@pytest_asyncio.fixture
async def viewer_user(db_session: AsyncSession) -> User:
    """Create a viewer user for testing."""
    user = User(
        id=uuid4(),
        email="testviewer@test.com",
        username="testviewer",
        full_name="Test Viewer",
        hashed_password=hash_password("testpass123"),
        role=UserRole.VIEWER,
        is_active=True,
        language="en",
    )
    db_session.add(user)
    await db_session.flush()
    return user


@pytest.fixture
def admin_token(admin_user: User) -> str:
    """Get JWT token for admin user."""
    return create_access_token(admin_user.id, admin_user.role.value)


@pytest.fixture
def manager_token(fleet_manager_user: User) -> str:
    """Get JWT token for fleet manager user."""
    return create_access_token(fleet_manager_user.id, fleet_manager_user.role.value)


@pytest.fixture
def viewer_token(viewer_user: User) -> str:
    """Get JWT token for viewer user."""
    return create_access_token(viewer_user.id, viewer_user.role.value)


def auth_header(token: str) -> dict:
    """Return Authorization header."""
    return {"Authorization": f"Bearer {token}"}
