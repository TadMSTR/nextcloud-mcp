"""OCS Provisioning API and Share API client."""

from __future__ import annotations

import httpx
import structlog

from .auth import get_admin_credentials
from .config import get_settings

log = structlog.get_logger()

_OCS_HEADERS = {"OCS-APIRequest": "true", "Accept": "application/json"}


def _base() -> str:
    return get_settings().url.rstrip("/")


async def ocs_get(path: str, params: dict | None = None) -> dict:
    user, pw = await get_admin_credentials()
    async with httpx.AsyncClient(auth=(user, pw), headers=_OCS_HEADERS) as client:
        r = await client.get(f"{_base()}{path}", params=params, timeout=15.0)
        r.raise_for_status()
        body = r.json()
    _check_ocs_status(body)
    return body["ocs"]


async def ocs_post(path: str, data: dict | None = None) -> dict:
    user, pw = await get_admin_credentials()
    async with httpx.AsyncClient(auth=(user, pw), headers=_OCS_HEADERS) as client:
        r = await client.post(f"{_base()}{path}", data=data or {}, timeout=15.0)
        r.raise_for_status()
        body = r.json()
    _check_ocs_status(body)
    return body["ocs"]


async def ocs_delete(path: str) -> dict:
    user, pw = await get_admin_credentials()
    async with httpx.AsyncClient(auth=(user, pw), headers=_OCS_HEADERS) as client:
        r = await client.delete(f"{_base()}{path}", timeout=15.0)
        r.raise_for_status()
        body = r.json()
    _check_ocs_status(body)
    return body["ocs"]


def _check_ocs_status(body: dict) -> None:
    # SECURITY[accepted]: OCS error messages are passed through to the caller. Nextcloud OCS
    # error messages are not sensitive (they describe API misuse, not internal state). Callers
    # are trusted MCP agents operating under scoped-mcp grants. Audit: 2026-06-21/nextcloud-mcp-2026-06.
    meta = body.get("ocs", {}).get("meta", {})
    status = meta.get("status", "")
    statuscode = meta.get("statuscode", 0)
    if status != "ok" and statuscode not in (100, 200):
        raise RuntimeError(f"OCS error {statuscode}: {meta.get('message', 'unknown')}")
