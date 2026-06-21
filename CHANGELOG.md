# Changelog

All notable changes will be documented here.

## [Unreleased]

### Security
- Redact `--value` argument from occ exec logs to prevent secret leakage (F-02)
- Validate WebDAV path and username in `_dav_url` to block traversal sequences (F-01)
- Fix `app_password_create` to generate password via `secrets.token_urlsafe` and inject via
  `docker exec -e OC_PASS` — eliminates broken `--password-from-env` pattern (F-04)
- Fix Vault KV v2 credential path: insert `/data/` and read `data.data` response (F-03)
- Remove forge-specific default URL from `config.py` (F-05)

### Added
- Initial FastMCP server scaffold
- 17 occ admin tools: status, maintenance mode, app management, config, file scan/cleanup,
  database maintenance, background jobs, upgrade check, security check, FTS indexing,
  external storage, notify_push self-test, log tail, system check
- 6 OCS Provisioning tools: user list/create/disable, group create/add-member,
  app password creation via occ
- 7 WebDAV + share tools: dav list/get/put/move/delete, share create/list/delete
- pydantic-settings config with NEXTCLOUD_ prefix
- Optional Vault credential resolution
- structlog JSON logging
- Optional OTLP telemetry (SigNoz/Jaeger)
- PM2 ecosystem config
- GitHub Actions CI (ruff lint + pytest on 3.11/3.12/3.13)
