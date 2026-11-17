import pytest
from pydantic import ValidationError

from app.core.config import INSECURE_ADMIN_TOKEN, Settings


@pytest.fixture(autouse=True)
def clean_env(monkeypatch):
    for name in ("DEBUG", "ADMIN_API_TOKEN", "TELEGRAM_BOT_TOKEN"):
        monkeypatch.delenv(name, raising=False)


def make(**overrides) -> Settings:
    return Settings(_env_file=None, **overrides)  # type: ignore[call-arg]


def test_debug_mode_allows_defaults():
    assert make(debug=True).admin_api_token == INSECURE_ADMIN_TOKEN


def test_production_rejects_default_admin_token():
    with pytest.raises(ValidationError):
        make(debug=False, telegram_bot_token="1:abc")


def test_production_rejects_short_admin_token():
    with pytest.raises(ValidationError):
        make(debug=False, admin_api_token="short", telegram_bot_token="1:abc")


def test_production_requires_bot_token():
    with pytest.raises(ValidationError):
        make(debug=False, admin_api_token="x" * 32)


def test_production_accepts_strong_config():
    settings = make(debug=False, admin_api_token="x" * 32, telegram_bot_token="1:abc")
    assert settings.debug is False
