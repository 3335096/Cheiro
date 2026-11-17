import logging
import tempfile
from io import BytesIO

from ebooklib import epub
from pypdf import PdfReader

logger = logging.getLogger(__name__)


def extract_epub(data: bytes) -> str:
    # ebooklib only reads from a filesystem path, so the upload goes through a short-lived temp file.
    with tempfile.NamedTemporaryFile(suffix=".epub") as tmp:
        tmp.write(data)
        tmp.flush()
        book = epub.read_epub(tmp.name, options={"ignore_ncx": True})
    parts: list[str] = []
    for item in book.get_items():
        if item.get_type() == 9:  # DOCUMENT
            try:
                parts.append(item.get_content().decode("utf-8", errors="ignore"))
            except Exception:
                logger.warning("Skipping unreadable EPUB item %s", item.get_name(), exc_info=True)
    return _strip_html_noise("\n".join(parts))


def extract_pdf_text(data: bytes) -> tuple[str, bool]:
    """Returns (text, needs_ocr). needs_ocr=True when extracted text is too short."""
    reader = PdfReader(BytesIO(data))
    texts: list[str] = []
    for page in reader.pages:
        texts.append(page.extract_text() or "")
    text = "\n".join(texts).strip()
    needs_ocr = len(text) < 400
    return text, needs_ocr


def _strip_html_noise(raw: str) -> str:
    import re

    text = re.sub(r"<script[^>]*>.*?</script>", " ", raw, flags=re.I | re.S)
    text = re.sub(r"<style[^>]*>.*?</style>", " ", text, flags=re.I | re.S)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def guess_language(sample: str) -> str:
    cyr = sum(1 for ch in sample if "\u0400" <= ch <= "\u04ff")
    return "ru" if cyr > len(sample) * 0.08 else "en"
