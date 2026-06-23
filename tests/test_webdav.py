"""Unit tests for WebDAV request construction."""

from __future__ import annotations

import base64

import httpx
import pytest
import respx

from tests.conftest import NEXTCLOUD_TEST_URL

DAV_BASE = f"{NEXTCLOUD_TEST_URL}/remote.php/dav/files/alice"

PROPFIND_XML = """<?xml version="1.0"?>
<d:multistatus xmlns:d="DAV:">
  <d:response><d:href>/remote.php/dav/files/alice/</d:href></d:response>
</d:multistatus>"""


@respx.mock
@pytest.mark.asyncio
async def test_dav_list():
    respx.route(method="PROPFIND", url=f"{DAV_BASE}/").mock(
        return_value=httpx.Response(207, text=PROPFIND_XML)
    )
    from nextcloud_mcp.server import dav_list

    result = await dav_list(username="alice", password="pw", path="")
    assert "<d:multistatus" in result


@respx.mock
@pytest.mark.asyncio
async def test_dav_get():
    content = b"Hello, Nextcloud!"
    respx.get(f"{DAV_BASE}/hello.txt").mock(return_value=httpx.Response(200, content=content))
    from nextcloud_mcp.server import dav_get

    result = await dav_get(username="alice", password="pw", path="hello.txt")
    assert base64.b64decode(result) == content


@respx.mock
@pytest.mark.asyncio
async def test_dav_put():
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
async def test_dav_move():
    respx.route(method="MOVE", url=f"{DAV_BASE}/old.txt").mock(
        return_value=httpx.Response(201)
    )
    from nextcloud_mcp.server import dav_move

    result = await dav_move(username="alice", password="pw", src="old.txt", dst="new.txt")
    assert "old.txt" in result
    assert "new.txt" in result


@respx.mock
@pytest.mark.asyncio
async def test_dav_delete():
    respx.delete(f"{DAV_BASE}/old.txt").mock(return_value=httpx.Response(204))
    from nextcloud_mcp.server import dav_delete

    result = await dav_delete(username="alice", password="pw", path="old.txt")
    assert "old.txt" in result
