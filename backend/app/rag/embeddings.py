from langchain_openai import OpenAIEmbeddings
from pydantic import SecretStr

from app.core.config import get_settings


def get_embedding_model() -> OpenAIEmbeddings:
    settings = get_settings()
    return OpenAIEmbeddings(
        model=settings.embedding_model,
        api_key=SecretStr(settings.openrouter_api_key or "not-set"),
        base_url=settings.openrouter_base_url,
        # Send raw text: OpenAI-compatible gateways such as OpenRouter reject pre-tokenized input.
        check_embedding_ctx_length=False,
        chunk_size=100,
    )
