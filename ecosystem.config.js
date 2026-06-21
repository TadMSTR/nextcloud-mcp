module.exports = {
  apps: [{
    name: "nextcloud-mcp",
    script: "/opt/appdata/nextcloud-mcp/run.sh",
    interpreter: "bash",
    env: {
      LOG_LEVEL: "INFO",
    },
    restart_delay: 5000,
    max_restarts: 10,
    watch: false,
  }]
};
