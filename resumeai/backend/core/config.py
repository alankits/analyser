from __future__ import annotations

from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # HuggingFace
    hf_api_token: str = ""
    hf_primary_model: str = "mistralai/Mistral-7B-Instruct-v0.3"
    hf_fallback_model: str = "HuggingFaceH4/zephyr-7b-beta"

    # Database — defaults to SQLite for local dev
    database_url: str = "sqlite+aiosqlite:///./resumeai.db"

    # Redis — fully optional; leave blank to disable caching
    redis_url: Optional[str] = None

    # CORS
    allowed_origins: str = "http://localhost:3000"

    # File upload limits
    max_file_size_mb: int = 5

    # Rate limiting
    rate_limit_per_minute: int = 10

    @property
    def allowed_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.allowed_origins.split(",") if origin.strip()]

    @property
    def max_file_size_bytes(self) -> int:
        return self.max_file_size_mb * 1024 * 1024

    @property
    def redis_enabled(self) -> bool:
        return bool(self.redis_url and self.redis_url.strip())


settings = Settings()
