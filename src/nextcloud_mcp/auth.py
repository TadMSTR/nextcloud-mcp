"""Credential resolution: env vars with optional Vault fallback."""

from __future__ import annotations

import httpx
import structlog

from .config import get_settings

log = structlog.get_logger()


async def get_admin_credentials() -> tuple[str, str]:
    """Return (username, password) for admin OCS/WebDAV calls."""
    cfg = get_settings()

    if cfg.vault_addr and cfg.vault_token:
        return await _vault_credentials(cfg)

    if not cfg.admin_password:
        raise RuntimeError(
            "NEXTCLOUD_ADMIN_PASSWORD is not set. "
            "Set the env var or configure NEXTCLOUD_VAULT_ADDR + NEXTCLOUD_VAULT_TOKEN."
        )
    return cfg.admin_user, cfg.admin_password


async def _vault_credentials(cfg: Settings) -> tuple[str, str]:  # noqa: F821
    headers = {"X-Vault-Token": cfg.vault_token}
    url = f"{cfg.vault_addr.rstrip('/')}/v1/{cfg.vault_admin_path.lstrip('/')}"
    log.debug("vault_credential_fetch", url=url)
    async with httpx.AsyncClient() as client:
        resp = await client.get(url, headers=headers, timeout=5.0)
        resp.raise_for_status()
    data = resp.json()["data"]["data"]  # KV v2 wraps secret under data.data
    return data["username"], data["password"]
