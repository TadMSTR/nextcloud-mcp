# Architecture — nextcloud-mcp

## Overview

```
MCP client (Claude agent)
        │
        ▼ stdio / HTTP
  nextcloud-mcp (FastMCP)
        │
  ┌─────┼─────────────────┐
  │     │                 │
  ▼     ▼                 ▼
 occ   OCS API        WebDAV
(docker exec)  (HTTP + Basic auth)  (HTTP + Basic auth)
  │     │                 │
  └──── Nextcloud container / API ──┘
```

## Modules

| Module | Responsibility |
|---|---|
| `config.py` | pydantic-settings; all env vars with NEXTCLOUD_ prefix |
| `auth.py` | Credential resolution: env vars → optional Vault |
| `occ.py` | `docker exec nextcloud occ` wrapper with timeout |
| `ocs.py` | OCS Provisioning + Share API HTTP client |
| `webdav.py` | WebDAV PROPFIND / GET / PUT / MOVE / DELETE |
| `server.py` | FastMCP app; all `@mcp.tool()` definitions |

## Credential model

Primary (required): `NEXTCLOUD_ADMIN_USER` + `NEXTCLOUD_ADMIN_PASSWORD` env vars.

Optional forge extension: Set `NEXTCLOUD_VAULT_ADDR` + `NEXTCLOUD_VAULT_TOKEN`
to resolve admin credentials from Vault at call time instead of env vars.
See `docs/forge.md` for the full forge setup.

## occ command

Runs as root inside the `nextcloud` container (`docker exec nextcloud occ`).
Root access is safe for occ — the Nextcloud container's PHP CLI runs as the
`abc` user internally when invoked this way.

## Port

`127.0.0.1:8500` — loopback only, behind scoped-mcp on forge.
