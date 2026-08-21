from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Central config for the whole fleet. Reads the repo-root .env once."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",  # ignore unrelated keys (e.g. GEMINI_API_KEY, which LiteLLM owns)
    )

    # --- Model gateway (agents talk ONLY to LiteLLM, never a provider directly) ---
    litellm_base_url: str = "http://localhost:4000"

    # --- Tracing: the one exporter endpoint that switches Langfuse <-> Phoenix ---
    otel_exporter_otlp_endpoint: str = "http://localhost:3000/api/public/otel"
    langfuse_public_key: str = ""
    langfuse_secret_key: str = ""


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
