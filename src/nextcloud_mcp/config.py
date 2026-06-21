"""Configuration via environment variables."""

from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="NEXTCLOUD_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    url: str = "https://nextcloud.helmforge.me"
    container: str = "nextcloud"
    occ_user: str = "abc"
    admin_user: str = "admin"
    admin_password: str = ""

    # Optional Vault extension
    vault_addr: str = ""
    vault_token: str = ""
    vault_admin_path: str = "secret/nextcloud/admin"

    log_level: str = "INFO"
    otel_exporter_otlp_endpoint: str = ""


_settings: Settings | None = None


def get_settings() -> Settings:
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
