"""Palm line CV adapter — noop until vendor API is chosen."""

import base64
from typing import Any

import httpx

from app.core.config import get_settings


async def extract_palm_features(image_bytes: bytes) -> dict[str, Any]:
    settings = get_settings()
    if not settings.palm_cv_api_url:
        return {
            "provider": "noop",
            "summary": (
                "Generic palm orientation detected; major lines not verified by CV API yet. "
                "Interpretation relies on RAG corpus and user photo framing."
            ),
        }

    async with httpx.AsyncClient(timeout=60.0) as client:
        resp = await client.post(
            settings.palm_cv_api_url,
            json={"image_base64": base64.b64encode(image_bytes).decode("ascii")},
        )
        resp.raise_for_status()
        return resp.json()
