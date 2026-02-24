"""Tests for reports API endpoints."""

import pytest
from httpx import AsyncClient

from tests.conftest import auth_header


@pytest.mark.asyncio
async def test_fleet_utilization(client: AsyncClient, admin_token: str):
    """GET /api/v1/reports/fleet-utilization returns 200 with utilization data."""
    response = await client.get(
        "/api/v1/reports/fleet-utilization",
        headers=auth_header(admin_token),
    )
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "active" in data
    assert "utilization_rate" in data


@pytest.mark.asyncio
async def test_tco_report(client: AsyncClient, admin_token: str):
    """GET /api/v1/reports/tco returns 200 with a list."""
    response = await client.get(
        "/api/v1/reports/tco",
        headers=auth_header(admin_token),
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_reports_require_auth(client: AsyncClient):
    """GET /api/v1/reports/tco without token returns 401."""
    response = await client.get("/api/v1/reports/tco")
    assert response.status_code == 401 or response.status_code == 403
