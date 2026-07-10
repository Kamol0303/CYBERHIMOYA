from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="CGA_", env_file=".env", extra="ignore")

    app_name: str = "Cyber Guardian AI API"
    environment: str = "dev"
    secret_key: str = "dev-only-change-me-cga-v1"
    access_token_ttl_seconds: int = 900
    refresh_token_ttl_seconds: int = 60 * 60 * 24 * 14
    guest_rate_limit_per_hour: int = 20
    feed_version: str = "20260710.2"
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"
    # sqlite:///./data/cga.db | sqlite:///:memory: | postgresql://user:pass@host:5432/cga
    database_url: str = "sqlite:///./data/cga.db"
    sqlite_fallback_path: str = "data/cga.db"
    public_base_url: str = "http://127.0.0.1:8000"
    # Optional override; otherwise uses app/data/keys/feed_ed25519_private.dev.b64
    feed_private_key_b64: str | None = None


settings = Settings()
