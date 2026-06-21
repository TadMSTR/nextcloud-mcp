"""Shared test fixtures."""

import pytest

import nextcloud_mcp.config as cfg_mod

NEXTCLOUD_TEST_URL = "https://nextcloud.example.com"


@pytest.fixture(autouse=True)
def reset_settings(monkeypatch):
    """Reset cached settings before each test and provide a consistent test URL."""
    monkeypatch.setenv("NEXTCLOUD_URL", NEXTCLOUD_TEST_URL)
    monkeypatch.setenv("NEXTCLOUD_ADMIN_PASSWORD", "test-password")
    cfg_mod._settings = None
    yield
    cfg_mod._settings = None
