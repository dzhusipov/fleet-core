"""Tests for authentication API endpoints."""

import pytest
from httpx import AsyncClient

from tests.conftest import auth_header


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient, admin_user):
    """POST /api/v1/auth/login with valid creds returns 200 and access_token."""
    response = await client.post(
        "/api/v1/auth/login",
        json={"username": "testadmin", "password": "testpass123"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_invalid_credentials(client: AsyncClient, admin_user):
    """POST /api/v1/auth/login with wrong password returns 401."""
    response = await client.post(
        "/api/v1/auth/login",
        json={"username": "testadmin", "password": "wrongpassword"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_me_authenticated(client: AsyncClient, admin_user, admin_token: str):
    """GET /api/v1/auth/me with valid token returns 200 and user info."""
    response = await client.get(
        "/api/v1/auth/me",
        headers=auth_header(admin_token),
    )
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testadmin"
    assert data["email"] == "testadmin@test.com"
    assert data["role"] == "admin"
    assert data["is_active"] is True


@pytest.mark.asyncio
async def test_get_me_unauthenticated(client: AsyncClient):
    """GET /api/v1/auth/me without token returns 401."""
    response = await client.get("/api/v1/auth/me")
    assert response.status_code == 401 or response.status_code == 403


@pytest.mark.asyncio
async def test_register_new_user(client: AsyncClient, admin_token: str):
    """POST /api/v1/auth/register creates a new user and returns 201."""
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "newuser@test.com",
            "username": "newuser",
            "full_name": "New User",
            "password": "securepass123",
            "role": "viewer",
            "language": "en",
        },
        headers=auth_header(admin_token),
    )
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "newuser"
    assert data["email"] == "newuser@test.com"
    assert data["role"] == "viewer"
