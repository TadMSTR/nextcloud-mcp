module.exports = {
  apps: [{
    name: "nextcloud-mcp",
    script: "/opt/venvs/nextcloud-mcp/bin/nextcloud-mcp",
    env: {
      LOG_LEVEL: "INFO",
      NEXTCLOUD_URL: "https://nextcloud.helmforge.me",
      NEXTCLOUD_CONTAINER: "nextcloud",
      NEXTCLOUD_ADMIN_USER: "admin",
      // NEXTCLOUD_ADMIN_PASSWORD: set in /opt/appdata/nextcloud-mcp/env or PM2 secret store
      // OTEL_EXPORTER_OTLP_ENDPOINT: "http://localhost:4317",
    },
    restart_delay: 5000,
    max_restarts: 10,
    watch: false,
  }]
};
