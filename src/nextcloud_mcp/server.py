"""nextcloud-mcp — FastMCP server for Nextcloud occ/OCS/WebDAV."""

from __future__ import annotations

import base64
import json
import os
from typing import Annotated, Literal

import structlog
from fastmcp import FastMCP

from .config import get_settings
from .occ import run_occ
from .ocs import ocs_delete, ocs_get, ocs_post
from .webdav import dav_delete as _dav_delete
from .webdav import dav_get as _dav_get
from .webdav import dav_move as _dav_move
from .webdav import dav_propfind
from .webdav import dav_put as _dav_put

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

structlog.configure(
    processors=[
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer(),
    ],
    wrapper_class=structlog.BoundLogger,
    logger_factory=structlog.PrintLoggerFactory(),
)
log = structlog.get_logger()

# ---------------------------------------------------------------------------
# Optional OTLP telemetry
# ---------------------------------------------------------------------------

_otel_endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "")
if _otel_endpoint:
    try:
        from opentelemetry import trace
        from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
        from opentelemetry.sdk.resources import Resource
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor

        _provider = TracerProvider(resource=Resource.create({"service.name": "nextcloud-mcp"}))
        _provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter(endpoint=_otel_endpoint)))
        trace.set_tracer_provider(_provider)
        log.info("otlp_enabled", endpoint=_otel_endpoint)
    except ImportError:
        log.warning("otlp_import_failed", hint="pip install 'nextcloud-mcp[telemetry]'")

mcp = FastMCP("nextcloud-mcp")


# ===========================================================================
# occ admin tools
# ===========================================================================


@mcp.tool()
async def occ_status() -> dict:
    """Return Nextcloud version, maintenance state, and instance ID."""
    return json.loads(await run_occ("status", "--output=json"))


@mcp.tool()
async def maintenance_mode(enable: bool | None = None) -> str:
    """
    Get or set maintenance mode.
    Omit enable to query current state; pass True/False to change it.
    """
    if enable is None:
        return await run_occ("maintenance:mode")
    return await run_occ("maintenance:mode", "--on" if enable else "--off")


@mcp.tool()
async def app_manage(
    action: Literal["list", "enable", "disable"],
    app: str = "",
) -> str:
    """List all apps or enable/disable a specific app by name."""
    if action == "list":
        return await run_occ("app:list", "--output=json")
    if not app:
        raise ValueError(f"app is required when action={action!r}")
    return await run_occ(f"app:{action}", app)


@mcp.tool()
async def config_get(
    scope: Literal["system", "app"],
    key: str,
    app_name: str = "",
) -> str:
    """Read a system or per-app config value. app_name required when scope='app'."""
    if scope == "system":
        return await run_occ("config:system:get", key)
    if not app_name:
        raise ValueError("app_name is required when scope='app'")
    return await run_occ("config:app:get", app_name, key)


@mcp.tool()
async def config_set(
    scope: Literal["system", "app"],
    key: str,
    value: str,
    app_name: str = "",
    value_type: Literal["string", "integer", "float", "boolean", "json", "array"] = "string",
) -> str:
    """
    Write a system or per-app config value.
    Incorrect values can break Nextcloud — prefer config_get before changing.
    """
    if scope == "system":
        return await run_occ("config:system:set", key, "--value", value, "--type", value_type)
    if not app_name:
        raise ValueError("app_name is required when scope='app'")
    return await run_occ("config:app:set", app_name, key, "--value", value, "--type", value_type)


@mcp.tool()
async def files_scan(path: str = "", all_users: bool = False) -> str:
    """
    Scan the filesystem and update the file cache.
    Provide path (e.g. 'alice/files/Documents') or set all_users=True.
    """
    if all_users:
        return await run_occ("files:scan", "--all")
    if path:
        return await run_occ("files:scan", "--path", path)
    raise ValueError("Provide path or set all_users=True")


@mcp.tool()
async def files_cleanup() -> str:
    """Remove orphaned file cache entries."""
    return await run_occ("files:cleanup")


@mcp.tool()
async def db_add_missing_indices() -> str:
    """Add missing database indices. Safe to run at any time; recommended after upgrades."""
    return await run_occ("db:add-missing-indices")


@mcp.tool()
async def db_convert_bigint() -> str:
    """Convert filecache IDs to bigint. Required after large installs or major upgrades."""
    return await run_occ("db:convert-filecache-bigint", "--no-interaction")


@mcp.tool()
async def background_jobs(action: Literal["mode", "run"] = "mode") -> str:
    """
    Query background job mode ('mode') or trigger a worker run ('run').
    'run' executes one pass of the background job queue.
    """
    if action == "mode":
        return await run_occ("background:mode")
    return await run_occ("background:job-worker", "default")


@mcp.tool()
async def upgrade_check() -> str:
    """Check for available Nextcloud core or app updates."""
    return await run_occ("update:check")


@mcp.tool()
async def security_check() -> str:
    """Run Nextcloud security advisory check against known CVEs."""
    return await run_occ("security:check")


@mcp.tool()
async def fulltextsearch_index(reset: bool = False) -> str:
    """
    Rebuild the full-text search index (OpenSearch).
    Set reset=True to wipe the index before reindexing.
    """
    args: list[str] = ["fulltextsearch:index"]
    if reset:
        args.append("--reset")
    return await run_occ(*args, timeout=300)


@mcp.tool()
async def external_storage_list() -> str:
    """List configured external storage mounts as JSON."""
    return await run_occ("files_external:list", "--output=json")


@mcp.tool()
async def notify_push_selftest() -> str:
    """Run the notify_push self-test to verify push notification connectivity."""
    return await run_occ("notify_push:self-test")


@mcp.tool()
async def log_tail(lines: int = 50) -> str:
    """Return the last N lines of nextcloud.log."""
    return await run_occ("log:tail", "--lines", str(lines))


@mcp.tool()
async def system_check() -> str:
    """Run an overall Nextcloud system health check."""
    return await run_occ("system:check")


# ===========================================================================
# OCS Provisioning API — sysadmin scope
# ===========================================================================


@mcp.tool()
async def user_list(search: str = "", limit: int = 100, offset: int = 0) -> dict:
    """List Nextcloud users. Optionally filter by search string."""
    params: dict = {"limit": limit, "offset": offset}
    if search:
        params["search"] = search
    return await ocs_get("/ocs/v1.php/cloud/users", params=params)


@mcp.tool()
async def user_create(
    username: str,
    password: str,
    email: str = "",
    display_name: str = "",
) -> dict:
    """Create a new Nextcloud user account."""
    data: dict = {"userid": username, "password": password}
    if email:
        data["email"] = email
    if display_name:
        data["displayName"] = display_name
    return await ocs_post("/ocs/v1.php/cloud/users", data=data)


@mcp.tool()
async def user_disable(username: str, disable: bool = True) -> str:
    """Enable or disable a Nextcloud user. disable=True to disable, False to re-enable."""
    action = "disable" if disable else "enable"
    result = await ocs_post(f"/ocs/v1.php/cloud/users/{username}/{action}")
    return result.get("meta", {}).get("message", "ok")


@mcp.tool()
async def group_create(group_id: str) -> dict:
    """Create a new Nextcloud user group."""
    return await ocs_post("/ocs/v1.php/cloud/groups", data={"groupid": group_id})


@mcp.tool()
async def group_add_member(group_id: str, username: str) -> str:
    """Add a user to an existing Nextcloud group."""
    result = await ocs_post(
        f"/ocs/v1.php/cloud/groups/{group_id}/users",
        data={"userid": username},
    )
    return result.get("meta", {}).get("message", "ok")


@mcp.tool()
async def app_password_create(username: str, label: str = "agent") -> str:
    """
    Generate an app password for a user via occ.
    Returns the password to the caller — never stored or logged by this server.
    Store it securely (e.g. Vault) immediately after receiving it.
    """
    out = await run_occ("user:add-app-password", username, "--password-from-env")
    # occ outputs the password on its own line; extract it
    for line in out.splitlines():
        stripped = line.strip()
        if stripped and not stripped.startswith("Generated"):
            return stripped
    # Fallback: return the full output (password is in it)
    return out


# ===========================================================================
# Files & shares — WebDAV + OCS Share API — per-agent scope
# ===========================================================================


@mcp.tool()
async def dav_list(username: str, password: str, path: str = "") -> str:
    """
    List files/directories at a WebDAV path for the given user.
    Returns raw WebDAV XML (PROPFIND response).
    """
    return await dav_propfind(username, password, path)


@mcp.tool()
async def dav_get(username: str, password: str, path: str) -> str:
    """Download a file. Returns base64-encoded content."""
    content = await _dav_get(username, password, path)
    return base64.b64encode(content).decode()


@mcp.tool()
async def dav_put(username: str, password: str, path: str, content_b64: str) -> str:
    """
    Upload a file. content_b64 must be base64-encoded bytes.
    Creates the file if it does not exist, overwrites if it does.
    """
    content = base64.b64decode(content_b64)
    await _dav_put(username, password, path, content)
    return f"Uploaded {len(content)} bytes to {path!r}"


@mcp.tool()
async def dav_move(username: str, password: str, src: str, dst: str) -> str:
    """Move or rename a file or directory within the user's WebDAV space."""
    await _dav_move(username, password, src, dst)
    return f"Moved {src!r} → {dst!r}"


@mcp.tool()
async def dav_delete(username: str, password: str, path: str) -> str:
    """Delete a file or directory from the user's WebDAV space."""
    await _dav_delete(username, password, path)
    return f"Deleted {path!r}"


@mcp.tool()
async def share_create(
    path: str,
    share_type: Annotated[int, "0=user, 1=group, 3=public link"] = 3,
    share_with: str = "",
    permissions: Annotated[int, "1=read,2=update,4=create,8=delete,16=share (additive)"] = 17,
    expire_date: str = "",
    note: str = "",
) -> dict:
    """
    Create a share via OCS. Authenticated as the admin user.
    For user/group shares (type 0/1), provide share_with.
    expire_date format: YYYY-MM-DD.
    """
    data: dict = {"path": path, "shareType": share_type, "permissions": permissions}
    if share_with:
        data["shareWith"] = share_with
    if expire_date:
        data["expireDate"] = expire_date
    if note:
        data["note"] = note
    return await ocs_post("/ocs/v2.php/apps/files_sharing/api/v1/shares", data=data)


@mcp.tool()
async def share_list(path: str = "", reshares: bool = False) -> dict:
    """List shares. Optionally filter by file path."""
    params: dict[str, str] = {"reshares": "true" if reshares else "false"}
    if path:
        params["path"] = path
    return await ocs_get("/ocs/v2.php/apps/files_sharing/api/v1/shares", params=params)


@mcp.tool()
async def share_delete(share_id: str) -> str:
    """Delete a share by its ID."""
    await ocs_delete(f"/ocs/v2.php/apps/files_sharing/api/v1/shares/{share_id}")
    return f"Deleted share {share_id}"


# ===========================================================================
# Entry point
# ===========================================================================


def main() -> None:
    cfg = get_settings()
    log.info("nextcloud_mcp_start", url=cfg.url, container=cfg.container)
    mcp.run()


if __name__ == "__main__":
    main()
