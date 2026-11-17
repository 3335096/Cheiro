"""OCR adapter — plug Google Vision / Textract without changing call sites."""

from app.core.config import get_settings


async def run_ocr(pdf_bytes: bytes) -> str:
    settings = get_settings()
    if settings.ocr_provider == "none":
        raise RuntimeError(
            "PDF appears to be scan-only but OCR_PROVIDER=none. "
            "Set OCR credentials or upload text-based PDF/EPUB."
        )
    # Placeholder for paid OCR integration (stage 1: interface + config).
    raise NotImplementedError(f"OCR provider {settings.ocr_provider} not configured yet")