"""Unit tests for WebDAV request construction."""

from __future__ import annotations

import base64

import httpx
import pytest
import respx

DAV_BASE = "https://nextcloud.helmforge.me/remote.php/dav/files/alice"

PROPFIND_XML = """<?xml version="1.0"?>
<d:multistatus xmlns:d="DAV:">
  <d:response><d:href>/remote.php/dav/files/alice/</d:href></d:response>
</d:multistatus>"""


@respx.mock
@pytest.mark.asyncio
async def test_dav_list(monkeypatch):
    monkeypatch.setenv("NEXTCLOUD_URL", "https://nextcloud.helmforge.me")
    monkeypatch.setenv("NEXTCLOUD_ADMIN_PASSWORD", "secret")
    # Reset cached settings
    import nextcloud_mcp.config as cfg_mod

    cfg_mod._settings = None

    respx.route(method="PROPFIND", url=f"{DAV_BASE}/").mock(
        return_value=httpx.Response(207, text=PROPFIND_XML)
    )
    from nextcloud_mcp.server import dav_list

    result = await dav_list(username="alice", password="pw", path="")
    assert "<d:multistatus" in result


@respx.mock
@pytest.mark.asyncio
async def test_dav_get(monkeypatch):
    monkeypatch.setenv("NEXTCLOUD_URL", "https://nextcloud.helmforge.me")
    monkeypatch.setenv("NEXTCLOUD_ADMIN_PASSWORD", "secret")
    import nextcloud_mcp.config as cfg_mod

    cfg_mod._settings = None

    content = b"Hello, Nextcloud!"
    respx.get(f"{DAV_BASE}/hello.txt").mock(return_value=httpx.Response(200, content=content))
    from nextcloud_mcp.server import dav_get

    result = await dav_get(username="alice", password="pw", path="hello.txt")
    assert base64.b64decode(result) == content


@respx.mock
@pytest.mark.asyncio
async def test_dav_put(monkeypatch):
    monkeypatch.setenv("NEXTCLOUD_URL", "https://nextcloud.helmforge.me")
    monkeypatch.setenv("NEXTCLOUD_ADMIN_PASSWORD", "secret")
    import nextcloud_mcp.config as cfg_mod

    cfg_mod._settings = None

    respx.put(f"{DAV_BASE}/upload.txt").mock(return_value=httpx.Response(201))
    from nextcloud_mcp.server import dav_put

    content = b"test content"
    result = await dav_put(
        username="alice",
        password="pw",
        path="upload.txt",
        content_b64=base64.b64encode(content).decode(),
    )
    assert "12 bytes" in result


@respx.mock
@pytest.mark.asyncio
async def test_dav_delete(monkeypatch):
    monkeypatch.setenv("NEXTCLOUD_URL", "https://nextcloud.helmforge.me")
    monkeypatch.setenv("NEXTCLOUD_ADMIN_PASSWORD", "secret")
    import nextcloud_mcp.config as cfg_mod

    cfg_mod._settings = None

    respx.delete(f"{DAV_BASE}/old.txt").mock(return_value=httpx.Response(204))
    from nextcloud_mcp.server import dav_delete

    result = await dav_delete(username="alice", password="pw", path="old.txt")
    assert "old.txt" in result
