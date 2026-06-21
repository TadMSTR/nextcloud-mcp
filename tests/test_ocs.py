"""Unit tests for OCS request construction."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import httpx
import pytest
import respx

from tests.conftest import NEXTCLOUD_TEST_URL

OCS_OK = {
    "ocs": {
        "meta": {"status": "ok", "statuscode": 100, "message": "OK"},
        "data": {},
    }
}


@pytest.fixture
def mock_get_creds():
    with patch(
        "nextcloud_mcp.ocs.get_admin_credentials",
        new_callable=AsyncMock,
        return_value=("admin", "secret"),
    ):
        yield


@respx.mock
@pytest.mark.asyncio
async def test_ocs_get_users(mock_get_creds):
    respx.get(f"{NEXTCLOUD_TEST_URL}/ocs/v1.php/cloud/users").mock(
        return_value=httpx.Response(
            200,
            json={
                "ocs": {
                    "meta": {"status": "ok", "statuscode": 100, "message": "OK"},
                    "data": {"users": ["alice", "bob"]},
                }
            },
        )
    )
    from nextcloud_mcp.server import user_list

    result = await user_list()
    assert "data" in result
    assert "alice" in result["data"]["users"]


@respx.mock
@pytest.mark.asyncio
async def test_ocs_post_user_create(mock_get_creds):
    respx.post(f"{NEXTCLOUD_TEST_URL}/ocs/v1.php/cloud/users").mock(
        return_value=httpx.Response(200, json=OCS_OK)
    )
    from nextcloud_mcp.server import user_create

    result = await user_create(username="testuser", password="pw123", email="test@example.com")
    assert result["meta"]["status"] == "ok"


@respx.mock
@pytest.mark.asyncio
async def test_share_create_public_link(mock_get_creds):
    respx.post(f"{NEXTCLOUD_TEST_URL}/ocs/v2.php/apps/files_sharing/api/v1/shares").mock(
        return_value=httpx.Response(
            200,
            json={
                "ocs": {
                    "meta": {"status": "ok", "statuscode": 200, "message": "OK"},
                    "data": {"id": "42", "url": f"{NEXTCLOUD_TEST_URL}/s/abc123"},
                }
            },
        )
    )
    from nextcloud_mcp.server import share_create

    result = await share_create(path="/Documents/report.pdf", share_type=3)
    assert result["data"]["id"] == "42"
    assert "url" in result["data"]


@respx.mock
@pytest.mark.asyncio
async def test_share_delete(mock_get_creds):
    respx.delete(f"{NEXTCLOUD_TEST_URL}/ocs/v2.php/apps/files_sharing/api/v1/shares/42").mock(
        return_value=httpx.Response(200, json=OCS_OK)
    )
    from nextcloud_mcp.server import share_delete

    result = await share_delete(share_id="42")
    assert "42" in result
