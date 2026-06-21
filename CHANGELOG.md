# Changelog

All notable changes will be documented here.

## [Unreleased]

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
