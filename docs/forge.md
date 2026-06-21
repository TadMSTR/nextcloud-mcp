# Forge Setup — nextcloud-mcp

This document covers forge-specific deployment: PM2, scoped-mcp integration,
and optional Vault credential brokering.

## Install

```bash
python3 -m venv /opt/venvs/nextcloud-mcp
/opt/venvs/nextcloud-mcp/bin/pip install nextcloud-mcp
# or from source:
/opt/venvs/nextcloud-mcp/bin/pip install -e /path/to/nextcloud-mcp
```

## PM2

```bash
# Create env file (chmod 600)
cat > /opt/appdata/nextcloud-mcp/env <<EOF
NEXTCLOUD_URL=https://nextcloud.helmforge.me
NEXTCLOUD_CONTAINER=nextcloud
NEXTCLOUD_ADMIN_USER=admin
NEXTCLOUD_ADMIN_PASSWORD=<admin-app-password>
OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317
EOF
chmod 600 /opt/appdata/nextcloud-mcp/env

# Set env in ecosystem.config.js, then:
pm2 start ecosystem.config.js
pm2 save
```

## Admin app password

Generate a Nextcloud app password for the admin account (not the primary password):

1. Log in to Nextcloud as admin
2. Settings → Security → Devices & sessions → Create new app password
3. Label it `mcp-admin` and store the generated password in `NEXTCLOUD_ADMIN_PASSWORD`

Or via occ after the server is running with a temporary password:
```bash
docker exec nextcloud occ user:add-app-password admin
```

## scoped-mcp manifest

Add to `~/.claude/manifests/nextcloud-mcp.yaml`:

```yaml
name: nextcloud-mcp
port: 8500
grants:
  sysadmin:
    tools: "*"
  developer:
    tools:
      - dav_list
      - dav_get
      - dav_put
      - dav_move
      - dav_delete
      - share_create
      - share_list
      - share_delete
  research:
    tools:
      - dav_list
      - dav_get
      - share_list
  writer:
    tools:
      - dav_list
      - dav_get
      - dav_put
      - share_create
      - share_list
  security:
    tools:
      - dav_list
      - occ_status
      - security_check
      - log_tail
```

## Optional Vault integration

When `NEXTCLOUD_VAULT_ADDR` and `NEXTCLOUD_VAULT_TOKEN` are set, admin credentials
are fetched from Vault at call time instead of env vars:

```
NEXTCLOUD_VAULT_ADDR=http://127.0.0.1:8200
NEXTCLOUD_VAULT_TOKEN=<token>
NEXTCLOUD_VAULT_ADMIN_PATH=secret/data/nextcloud/admin
```

The secret at that path must have `username` and `password` keys (KV v2 path — include `/data/` between the mount and key name):
```bash
vault kv put secret/nextcloud/admin username=admin password=<app-password>
```

## Per-agent file access

Each agent that needs file access should have its own Nextcloud user and app password.
Store the app password in scoped-mcp's per-agent env (or Vault) and pass it as the
`password` parameter to `dav_*` and `share_*` tools.

Generate app passwords via:
```
app_password_create(username="agent-developer", label="forge-developer")
```
