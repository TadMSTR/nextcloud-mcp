# nextcloud-mcp

[![CI](https://github.com/TadMSTR/nextcloud-mcp/actions/workflows/ci.yml/badge.svg)](https://github.com/TadMSTR/nextcloud-mcp/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/nextcloud-mcp)](https://pypi.org/project/nextcloud-mcp/)
[![Built with Claude Code](https://img.shields.io/badge/Built%20with-Claude%20Code-blueviolet)](https://claude.ai/claude-code)

FastMCP server for Nextcloud — exposes `occ` admin commands, OCS provisioning,
and WebDAV file operations as MCP tools.

## Overview

nextcloud-mcp wraps three Nextcloud API surfaces:

- **`occ` admin** — CLI commands executed via `docker exec` inside the Nextcloud container.
  Covers version/health, maintenance mode, app management, config, file scanning,
  database maintenance, background jobs, FTS indexing, external storage, and log tailing.
- **OCS Provisioning API** — HTTP-based user and group management, plus app password generation.
- **WebDAV + Share API** — per-user file list/get/put/move/delete, and share create/list/delete.

Intended for homelab and self-hosted operators who want agent-driven Nextcloud administration.
`occ` and OCS tools are restricted to privileged agents; WebDAV/share tools are available
per-agent with per-call credentials.

## Tools

### occ Admin (17 tools)

| Tool | Description | Key Parameters | Returns |
|------|-------------|----------------|---------|
| `occ_status` | Nextcloud version, maintenance state, instance ID | — | `dict` |
| `maintenance_mode` | Get or set maintenance mode | `enable: bool\|None` | `str` |
| `app_manage` | List apps or enable/disable one | `action: list\|enable\|disable`, `app: str` | `str` |
| `config_get` | Read a system or per-app config value | `scope: system\|app`, `key`, `app_name` | `str` |
| `config_set` | Write a system or per-app config value | `scope`, `key`, `value`, `value_type` | `str` |
| `files_scan` | Scan filesystem and update file cache | `path: str`, `all_users: bool` | `str` |
| `files_cleanup` | Remove orphaned file cache entries | — | `str` |
| `db_add_missing_indices` | Add missing database indices | — | `str` |
| `db_convert_bigint` | Convert filecache IDs to bigint | — | `str` |
| `background_jobs` | Query job mode or trigger a worker run | `action: mode\|run` | `str` |
| `upgrade_check` | Check for available core or app updates | — | `str` |
| `security_check` | Run security advisory check against known CVEs | — | `str` |
| `fulltextsearch_index` | Rebuild full-text search index (OpenSearch) | `reset: bool` | `str` |
| `external_storage_list` | List configured external storage mounts | — | `str` (JSON) |
| `notify_push_selftest` | Verify push notification connectivity | — | `str` |
| `log_tail` | Return last N lines of nextcloud.log | `lines: int` (default 50) | `str` |
| `system_check` | Run overall system health check | — | `str` |

> `config_set` can break Nextcloud — always `config_get` before writing.
> `fulltextsearch_index --reset` wipes the OpenSearch index; takes time on large instances.

### OCS Provisioning (6 tools)

| Tool | Description | Key Parameters | Returns |
|------|-------------|----------------|---------|
| `user_list` | List users, optionally filtered | `search`, `limit`, `offset` | `dict` |
| `user_create` | Create a new user account | `username`, `password`, `email`, `display_name` | `dict` |
| `user_disable` | Enable or disable a user | `username`, `disable: bool` | `str` |
| `group_create` | Create a user group | `group_id` | `dict` |
| `group_add_member` | Add user to a group | `group_id`, `username` | `str` |
| `app_password_create` | Generate an app password via occ | `username`, `label` | `str` (password, one-time) |

> `app_password_create` returns the password exactly once — store it in Vault immediately.

### WebDAV + Shares (8 tools)

WebDAV tools authenticate as the calling agent's own Nextcloud user (pass `username`/`password`
per call). Share tools authenticate as the admin user — required for cross-user share management.

| Tool | Description | Key Parameters | Returns |
|------|-------------|----------------|---------|
| `dav_list` | List files/directories at a path | `username`, `password`, `path` | `str` (XML) |
| `dav_get` | Download a file | `username`, `password`, `path` | `str` (base64) |
| `dav_put` | Upload a file | `username`, `password`, `path`, `content_b64` | `str` |
| `dav_move` | Move or rename a file/directory | `username`, `password`, `src`, `dst` | `str` |
| `dav_delete` | Delete a file or directory | `username`, `password`, `path` | `str` |
| `share_create` | Create a share (user/group/public link) | `path`, `share_type`, `share_with`, `permissions`, `expire_date` | `dict` |
| `share_list` | List shares, optionally by path | `path`, `reshares` | `dict` |
| `share_delete` | Delete a share by ID | `share_id` | `str` |

WebDAV paths are relative to the user's file root — no leading slash needed.
`dav_get`/`dav_put` use base64 encoding for binary content.

## Environment Variables

| Variable | Required | Default | Purpose |
|----------|----------|---------|---------|
| `NEXTCLOUD_URL` | Yes | — | Nextcloud base URL (e.g. `https://nextcloud.example.com`) |
| `NEXTCLOUD_CONTAINER` | No | `nextcloud` | Docker container name for `occ` exec |
| `NEXTCLOUD_ADMIN_USER` | No | `admin` | Admin username for OCS and share tools |
| `NEXTCLOUD_ADMIN_PASSWORD` | Yes* | — | Admin app password (*unless Vault is configured) |
| `NEXTCLOUD_VAULT_ADDR` | No | — | Vault address (enables credential brokering) |
| `NEXTCLOUD_VAULT_TOKEN` | No | — | Vault token (required when `VAULT_ADDR` is set) |
| `NEXTCLOUD_VAULT_ADMIN_PATH` | No | `secret/data/nextcloud/admin` | Vault KV v2 path for admin credentials |
| `OTEL_EXPORTER_OTLP_ENDPOINT` | No | — | OTLP trace endpoint (e.g. `http://localhost:4317`) |
| `LOG_LEVEL` | No | `INFO` | Log verbosity |

FastMCP transport (HTTP mode):

| Variable | Default | Purpose |
|----------|---------|---------|
| `FASTMCP_TRANSPORT` | `stdio` | Set to `streamable-http` for HTTP server mode |
| `FASTMCP_PORT` | `8000` | Bind port (HTTP mode) |
| `FASTMCP_HOST` | `127.0.0.1` | Bind host (HTTP mode) |

## Installation

**Prerequisites:** Python 3.11+, Docker (for `occ` tools)

```bash
pip install nextcloud-mcp
```

Or from source:

```bash
git clone https://github.com/TadMSTR/nextcloud-mcp.git
cd nextcloud-mcp
python3 -m venv .venv
.venv/bin/pip install -e .
```

With optional OTLP telemetry:

```bash
pip install 'nextcloud-mcp[telemetry]'
```

**Quickstart:**

```bash
NEXTCLOUD_URL=https://nextcloud.example.com \
NEXTCLOUD_ADMIN_PASSWORD=<app-password> \
nextcloud-mcp
```

## Deployment

### PM2

Use `ecosystem.config.js` in the repo root:

```bash
# Create env file
mkdir -p /opt/appdata/nextcloud-mcp
cat > /opt/appdata/nextcloud-mcp/env <<'EOF'
NEXTCLOUD_URL=https://nextcloud.example.com
NEXTCLOUD_CONTAINER=nextcloud
NEXTCLOUD_ADMIN_USER=admin
NEXTCLOUD_ADMIN_PASSWORD=<app-password>
FASTMCP_TRANSPORT=streamable-http
FASTMCP_PORT=8500
FASTMCP_HOST=127.0.0.1
OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317
EOF
chmod 600 /opt/appdata/nextcloud-mcp/env

# Load env and start
export $(grep -v '^#' /opt/appdata/nextcloud-mcp/env | xargs)
pm2 start ecosystem.config.js
pm2 save
```

### Admin app password

Generate a Nextcloud app password for the admin account:

1. Log in to Nextcloud as admin
2. Settings → Security → Devices & sessions → Create new app password, label it `mcp-admin`

Or via occ after initial setup with a temporary password.

### scoped-mcp wiring

Example `~/.claude/manifests/nextcloud-mcp.yaml`:

```yaml
name: nextcloud-mcp
port: 8500
grants:
  sysadmin:
    tools: "*"
  developer:
    tools: [dav_list, dav_get, dav_put, dav_move, dav_delete, share_create, share_list, share_delete]
  research:
    tools: [dav_list, dav_get, share_list]
  writer:
    tools: [dav_list, dav_get, dav_put, share_create, share_list]
  security:
    tools: [dav_list, occ_status, security_check, log_tail]
```

### Vault integration (optional)

When `NEXTCLOUD_VAULT_ADDR` and `NEXTCLOUD_VAULT_TOKEN` are set, admin credentials are
fetched from Vault at call time instead of env vars:

```bash
# Store credentials (KV v2 — path includes /data/)
vault kv put secret/nextcloud/admin username=admin password=<app-password>
```

```
NEXTCLOUD_VAULT_ADDR=http://127.0.0.1:8200
NEXTCLOUD_VAULT_TOKEN=<token>
NEXTCLOUD_VAULT_ADMIN_PATH=secret/data/nextcloud/admin
```

### Per-agent file access

Each agent should use its own Nextcloud account and app password, passed per-call to
`dav_*` and `share_*` tools. Generate app passwords via:

```python
app_password_create(username="agent-developer", label="forge-developer")
```

Store the returned password in Vault immediately — it is not logged or stored by this server.

## Observability

- **Logs:** structlog JSON to stdout. Level controlled by `LOG_LEVEL`.
- **Traces:** set `OTEL_EXPORTER_OTLP_ENDPOINT` (gRPC); requires `nextcloud-mcp[telemetry]`.
- **occ arg redaction:** `--value` arguments are replaced with `[REDACTED]` in log output.

## Forge deployment

See [docs/forge.md](docs/forge.md) for the full forge setup walkthrough: venv install, PM2,
scoped-mcp manifest details, and Vault credential brokering.

## License

MIT
