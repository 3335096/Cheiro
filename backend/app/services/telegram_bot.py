import httpx

from app.core.config import get_settings


async def send_message(chat_id: str, text: str) -> None:
    settings = get_settings()
    if not settings.telegram_bot_token:
        return
    if len(text) > 4000:
        text = text[:3990] + "…"
    url = f"https://api.telegram.org/bot{settings.telegram_bot_token}/sendMessage"
    async with httpx.AsyncClient(timeout=30.0) as client:
        await client.post(url, json={"chat_id": chat_id, "text": text})