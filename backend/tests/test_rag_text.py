from io import BytesIO

from ebooklib import epub
from pypdf import PdfWriter

from app.rag.chunking import split_text
from app.rag.extract import extract_epub, extract_pdf_text, guess_language


def build_epub(chapters: dict[str, str]) -> bytes:
    book = epub.EpubBook()
    book.set_identifier("test-book")
    book.set_title("Test")
    book.set_language("en")
    items = []
    for idx, (title, body) in enumerate(chapters.items()):
        chapter = epub.EpubHtml(title=title, file_name=f"ch{idx}.xhtml", lang="en")
        chapter.content = f"<html><body><h1>{title}</h1><p>{body}</p><script>evil()</script></body></html>"
        book.add_item(chapter)
        items.append(chapter)
    book.toc = tuple(items)
    book.spine = ["nav", *items]
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())
    buffer = BytesIO()
    epub.write_epub(buffer, book)
    return buffer.getvalue()


def test_extract_epub_returns_clean_text_without_markup_or_scripts():
    data = build_epub({"Life line": "The life line curves around the thumb."})

    text = extract_epub(data)

    assert "life line curves around the thumb" in text.lower()
    assert "<p>" not in text
    assert "evil()" not in text


def test_pdf_without_text_layer_requests_ocr():
    writer = PdfWriter()
    writer.add_blank_page(width=200, height=200)
    buffer = BytesIO()
    writer.write(buffer)

    text, needs_ocr = extract_pdf_text(buffer.getvalue())

    assert text == ""
    assert needs_ocr is True


def test_guess_language_detects_russian_and_english():
    assert guess_language("Линия жизни огибает бугор большого пальца") == "ru"
    assert guess_language("The heart line shows emotional tendencies") == "en"


def test_split_text_respects_chunk_size_and_keeps_all_content():
    sentence = "The head line reflects thinking style. "
    text = sentence * 200

    chunks = split_text(text)

    assert len(chunks) > 1
    assert all(len(chunk) <= 1000 for chunk in chunks)
    assert "head line" in chunks[0]
