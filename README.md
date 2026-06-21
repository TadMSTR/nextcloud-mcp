# nextcloud-mcp

[![CI](https://github.com/TadMSTR/nextcloud-mcp/actions/workflows/ci.yml/badge.svg)](https://github.com/TadMSTR/nextcloud-mcp/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/nextcloud-mcp)](https://pypi.org/project/nextcloud-mcp/)
[![Built with Claude Code](https://img.shields.io/badge/Built%20with-Claude%20Code-blueviolet)](https://claude.ai/claude-code)

FastMCP server for Nextcloud — exposes `occ` admin commands, OCS provisioning,
and WebDAV file operations as MCP tools.

## Features

- **17 occ admin tools** — version check, maintenance mode, app management, config read/write,
  file scan, database maintenance, background jobs, FTS indexing, security advisory check,
  log tail, and system health
- **6 OCS provisioning tools** — user and group management, app password generation
- **7 WebDAV + share tools** — list, get, put, move, delete files; create/list/delete shares

## Quick start

```bash
pip install nextcloud-mcp
```

```
NEXTCLOUD_URL=https://your-nextcloud.example.com
NEXTCLOUD_CONTAINER=nextcloud
NEXTCLOUD_ADMIN_USER=admin
NEXTCLOUD_ADMIN_PASSWORD=<app-password>
nextcloud-mcp
```

## Configuration

| Variable | Default | Description |
|---|---|---|
| `NEXTCLOUD_URL` | `https://nextcloud.helmforge.me` | Nextcloud base URL |
| `NEXTCLOUD_CONTAINER` | `nextcloud` | Docker container name |
| `NEXTCLOUD_ADMIN_USER` | `admin` | Admin username |
| `NEXTCLOUD_ADMIN_PASSWORD` | _(required)_ | Admin app password |
| `OTEL_EXPORTER_OTLP_ENDPOINT` | _(off)_ | OTLP trace endpoint |
| `LOG_LEVEL` | `INFO` | Log verbosity |

Optional Vault integration: set `NEXTCLOUD_VAULT_ADDR` + `NEXTCLOUD_VAULT_TOKEN`
to fetch credentials from HashiCorp Vault instead of env vars.

## Forge deployment

See [docs/forge.md](docs/forge.md) for PM2, scoped-mcp, and Vault setup.

## License

MIT
