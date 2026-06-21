"""WebDAV file operations (PROPFIND, GET, PUT, MOVE, DELETE)."""

from __future__ import annotations

import re
import urllib.parse

import httpx
import structlog

from .config import get_settings

log = structlog.get_logger()

_DAV_USER_RE = re.compile(r"^[a-zA-Z0-9_.@-]+$")


def _validate_dav_path(path: str) -> str:
    """Reject traversal sequences — raw (../) and percent-encoded (%2e, %2f)."""
    if "%2e" in path.lower() or "%2f" in path.lower():
        raise ValueError("Invalid path: percent-encoded traversal not allowed")
    decoded = urllib.parse.unquote(path)
    if ".." in decoded.replace("\\", "/").split("/"):
        raise ValueError("Invalid path: traversal sequences not allowed")
    return path.strip("/")


def _dav_url(username: str, path: str = "") -> str:
    if not _DAV_USER_RE.match(username):
        raise ValueError(f"Invalid username {username!r}: must match {_DAV_USER_RE.pattern}")
    clean = _validate_dav_path(path)
    base = get_settings().url.rstrip("/")
    return f"{base}/remote.php/dav/files/{username}/{clean}"


async def dav_propfind(username: str, password: str, path: str = "") -> str:
    """List directory — returns raw WebDAV XML."""
    url = _dav_url(username, path)
    log.debug("dav_propfind", url=url)
    async with httpx.AsyncClient(auth=(username, password)) as client:
        r = await client.request("PROPFIND", url, headers={"Depth": "1"}, timeout=15.0)
        r.raise_for_status()
        return r.text


async def dav_get(username: str, password: str, path: str) -> bytes:
    """Download file content."""
    url = _dav_url(username, path)
    log.debug("dav_get", url=url)
    async with httpx.AsyncClient(auth=(username, password)) as client:
        r = await client.get(url, timeout=60.0)
        r.raise_for_status()
        return r.content


async def dav_put(username: str, password: str, path: str, content: bytes) -> None:
    """Upload file content, creating parent directories as needed."""
    url = _dav_url(username, path)
    log.debug("dav_put", url=url, size=len(content))
    async with httpx.AsyncClient(auth=(username, password)) as client:
        r = await client.put(url, content=content, timeout=60.0)
        r.raise_for_status()


async def dav_move(username: str, password: str, src: str, dst: str) -> None:
    """Move or rename a file/directory."""
    src_url = _dav_url(username, src)
    dst_url = _dav_url(username, dst)
    log.debug("dav_move", src=src_url, dst=dst_url)
    async with httpx.AsyncClient(auth=(username, password)) as client:
        r = await client.request(
            "MOVE",
            src_url,
            headers={"Destination": dst_url, "Overwrite": "F"},
            timeout=15.0,
        )
        r.raise_for_status()


async def dav_delete(username: str, password: str, path: str) -> None:
    """Delete a file or directory."""
    url = _dav_url(username, path)
    log.debug("dav_delete", url=url)
    async with httpx.AsyncClient(auth=(username, password)) as client:
        r = await client.delete(url, timeout=15.0)
        r.raise_for_status()
