from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "CHEIRO"
    debug: bool = False

    database_url: str = "postgresql+asyncpg://cheiro:cheiro@localhost:5432/cheiro"
    redis_url: str = "redis://localhost:6379/0"

    telegram_bot_token: str = ""
    telegram_webapp_url: str = "http://localhost:5173"

    openrouter_api_key: str = ""
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    llm_model: str = "openai/gpt-4o-mini"
    embedding_model: str = "openai/text-embedding-3-small"

    admin_api_token: str = "dev-admin-change-me"

    ocr_provider: str = "none"  # none | gcv | textract

    palm_cv_api_url: str = ""
    zhivo_crm_webhook_url: str = ""

    rag_chunk_size: int = 1000
    rag_chunk_overlap: int = 150
    rag_top_k: int = 8

    system_prompt_path: str = "app/rag/prompts/system_default.txt"


@lru_cache
def get_settings() -> Settings:
    return Settings()