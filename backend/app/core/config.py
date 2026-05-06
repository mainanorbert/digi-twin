"""Application settings loaded from environment variables."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Runtime configuration for OpenRouter and HTTP defaults.

    Attributes:
        openrouter_api_key: Secret API key for OpenRouter (OpenAI-compatible).
        openrouter_base_url: Base URL for chat completions.
        openrouter_model: Model id, e.g. openai/gpt-4o-mini.
        openrouter_http_referer: Optional Referer header required by some providers.
        openrouter_x_title: Optional X-Title header for OpenRouter analytics.
        cors_allowed_origins: Comma-separated frontend origins allowed to call the API.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    openrouter_api_key: str = ""
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    openrouter_model: str = "openai/gpt-4o-mini"
    openrouter_http_referer: str = "https://localhost"
    openrouter_x_title: str = "Digi-Twini API"
    cors_allowed_origins: str = "http://localhost:3000,http://127.0.0.1:3000"

    def cors_allowed_origins_list(self) -> list[str]:
        """
        Parse comma-separated CORS origins from the environment.

        Returns:
            Normalized non-empty origins.
        """
        return [
            origin.strip().rstrip("/")
            for origin in self.cors_allowed_origins.split(",")
            if origin.strip()
        ]
