import hashlib
import hmac
import json
from urllib.parse import urlencode

from app.services.telegram_auth import validate_init_data

BOT_TOKEN = "123456:TEST-TOKEN"


def sign_init_data(fields: dict[str, str], bot_token: str = BOT_TOKEN) -> str:
    check_string = "\n".join(f"{k}={v}" for k, v in sorted(fields.items()))
    secret = hmac.new(b"WebAppData", bot_token.encode(), hashlib.sha256).digest()
    digest = hmac.new(secret, check_string.encode(), hashlib.sha256).hexdigest()
    return urlencode({**fields, "hash": digest})


def test_valid_init_data_returns_parsed_user():
    user = {"id": 42, "first_name": "Ada"}
    init_data = sign_init_data({"user": json.dumps(user), "auth_date": "1700000000"})

    parsed = validate_init_data(init_data, BOT_TOKEN)

    assert parsed is not None
    assert parsed["user"]["id"] == 42


def test_tampered_payload_is_rejected():
    init_data = sign_init_data({"user": json.dumps({"id": 42}), "auth_date": "1700000000"})
    tampered = init_data.replace("%22id%22%3A+42", "%22id%22%3A+43")

    assert tampered != init_data
    assert validate_init_data(tampered, BOT_TOKEN) is None


def test_wrong_bot_token_is_rejected():
    init_data = sign_init_data({"user": json.dumps({"id": 1})}, bot_token="999:OTHER")

    assert validate_init_data(init_data, BOT_TOKEN) is None


def test_missing_hash_or_empty_input_is_rejected():
    assert validate_init_data("", BOT_TOKEN) is None
    assert validate_init_data("user=%7B%7D", BOT_TOKEN) is None
    assert validate_init_data("hash=abc", "") is None
