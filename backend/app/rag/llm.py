from pathlib import Path

from langchain_openai import ChatOpenAI
from pydantic import SecretStr

from app.core.config import get_settings


def get_llm() -> ChatOpenAI:
    settings = get_settings()
    return ChatOpenAI(
        model=settings.llm_model,
        api_key=SecretStr(settings.openrouter_api_key or "not-set"),
        base_url=settings.openrouter_base_url,
        temperature=0.4,
    )


def load_system_prompt() -> str:
    settings = get_settings()
    path = Path(settings.system_prompt_path)
    if path.is_file():
        return path.read_text(encoding="utf-8")
    return "You are CHEIRO chiromancy assistant."
