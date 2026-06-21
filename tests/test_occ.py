"""Unit tests for occ command construction."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest


@pytest.fixture
def mock_run_occ():
    with patch("nextcloud_mcp.server.run_occ", new_callable=AsyncMock) as m:
        yield m


@pytest.mark.asyncio
async def test_occ_status(mock_run_occ):
    mock_run_occ.return_value = '{"installed": true, "version": "34.0.0.0", "versionstring": "34.0.0", "edition": "", "maintenance": false, "needsDbUpgrade": false}'
    from nextcloud_mcp.server import occ_status

    result = await occ_status()
    mock_run_occ.assert_called_once_with("status", "--output=json")
    assert result["installed"] is True
    assert result["maintenance"] is False


@pytest.mark.asyncio
async def test_maintenance_mode_get(mock_run_occ):
    mock_run_occ.return_value = "Maintenance mode is currently disabled"
    from nextcloud_mcp.server import maintenance_mode

    result = await maintenance_mode()
    mock_run_occ.assert_called_once_with("maintenance:mode")
    assert "disabled" in result


@pytest.mark.asyncio
async def test_maintenance_mode_enable(mock_run_occ):
    mock_run_occ.return_value = "Maintenance mode enabled"
    from nextcloud_mcp.server import maintenance_mode

    await maintenance_mode(enable=True)
    mock_run_occ.assert_called_once_with("maintenance:mode", "--on")


@pytest.mark.asyncio
async def test_maintenance_mode_disable(mock_run_occ):
    mock_run_occ.return_value = "Maintenance mode disabled"
    from nextcloud_mcp.server import maintenance_mode

    await maintenance_mode(enable=False)
    mock_run_occ.assert_called_once_with("maintenance:mode", "--off")


@pytest.mark.asyncio
async def test_app_manage_list(mock_run_occ):
    mock_run_occ.return_value = '{"enabled": {}, "disabled": {}}'
    from nextcloud_mcp.server import app_manage

    await app_manage(action="list")
    mock_run_occ.assert_called_once_with("app:list", "--output=json")


@pytest.mark.asyncio
async def test_app_manage_enable(mock_run_occ):
    mock_run_occ.return_value = "calendar enabled"
    from nextcloud_mcp.server import app_manage

    await app_manage(action="enable", app="calendar")
    mock_run_occ.assert_called_once_with("app:enable", "calendar")


@pytest.mark.asyncio
async def test_app_manage_requires_app(mock_run_occ):
    from nextcloud_mcp.server import app_manage

    with pytest.raises(ValueError, match="app is required"):
        await app_manage(action="enable")


@pytest.mark.asyncio
async def test_config_get_system(mock_run_occ):
    mock_run_occ.return_value = "https://nextcloud.helmforge.me"
    from nextcloud_mcp.server import config_get

    result = await config_get(scope="system", key="overwrite.cli.url")
    mock_run_occ.assert_called_once_with("config:system:get", "overwrite.cli.url")
    assert "nextcloud" in result


@pytest.mark.asyncio
async def test_config_get_app_requires_app_name(mock_run_occ):
    from nextcloud_mcp.server import config_get

    with pytest.raises(ValueError, match="app_name is required"):
        await config_get(scope="app", key="some_key")


@pytest.mark.asyncio
async def test_files_scan_path(mock_run_occ):
    mock_run_occ.return_value = "Starting scan... done"
    from nextcloud_mcp.server import files_scan

    await files_scan(path="alice/files")
    mock_run_occ.assert_called_once_with("files:scan", "--path", "alice/files")


@pytest.mark.asyncio
async def test_files_scan_all_users(mock_run_occ):
    mock_run_occ.return_value = "Scanning all"
    from nextcloud_mcp.server import files_scan

    await files_scan(all_users=True)
    mock_run_occ.assert_called_once_with("files:scan", "--all")


@pytest.mark.asyncio
async def test_files_scan_requires_target(mock_run_occ):
    from nextcloud_mcp.server import files_scan

    with pytest.raises(ValueError):
        await files_scan()


@pytest.mark.asyncio
async def test_db_add_missing_indices(mock_run_occ):
    mock_run_occ.return_value = "Adding index... done"
    from nextcloud_mcp.server import db_add_missing_indices

    await db_add_missing_indices()
    mock_run_occ.assert_called_once_with("db:add-missing-indices")


@pytest.mark.asyncio
async def test_fulltextsearch_index_reset(mock_run_occ):
    mock_run_occ.return_value = "Indexing..."
    from nextcloud_mcp.server import fulltextsearch_index

    await fulltextsearch_index(reset=True)
    mock_run_occ.assert_called_once_with("fulltextsearch:index", "--reset", timeout=300)
