# AGENTS.md — nextcloud-mcp

## What this server does

Exposes Nextcloud operations as MCP tools:

- **occ admin** — version check, maintenance mode, app management, config, file scan,
  database maintenance, background jobs, FTS indexing, security check, log tail
- **OCS provisioning** — user and group management, app password generation
- **WebDAV file ops** — list, get, put, move, delete
- **Share management** — create/list/delete public links and user/group shares

## Tool groups

| Group | Scope | Tools |
|---|---|---|
| occ-admin | sysadmin | occ_status, maintenance_mode, app_manage, config_get, config_set, files_scan, files_cleanup, db_add_missing_indices, db_convert_bigint, background_jobs, upgrade_check, security_check, fulltextsearch_index, external_storage_list, notify_push_selftest, log_tail, system_check |
| ocs-provisioning | sysadmin | user_list, user_create, user_disable, group_create, group_add_member, app_password_create |
| files | per-agent | dav_list, dav_get, dav_put, dav_move, dav_delete, share_create, share_list, share_delete |

## scoped-mcp integration (forge)

In `~/.claude/manifests/`:

```yaml
nextcloud-mcp:
  port: 8500
  grants:
    sysadmin:
      - occ-admin
      - ocs-provisioning
      - files
    developer:
      - files
    research:
      - files
    writer:
      - files
    security:
      - files
```

## Important notes

- `config_set` can break Nextcloud. Use `config_get` to read before writing.
- `app_password_create` returns the password once. Store it in Vault immediately.
- `fulltextsearch_index --reset` wipes and rebuilds the full OpenSearch index. Takes time.
- `dav_get` / `dav_put` use base64 encoding for binary content.
- WebDAV paths are relative to the user's file root (no leading slash needed).
