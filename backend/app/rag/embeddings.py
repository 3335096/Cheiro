from langchain_openai import OpenAIEmbeddings

from app.core.config import get_settings


def get_embedding_model() -> OpenAIEmbeddings:
    settings = get_settings()
    return OpenAIEmbeddings(
        model=settings.embedding_model,
        api_key=settings.openrouter_api_key or "not-set",
        base_url=settings.openrouter_base_url,
    )