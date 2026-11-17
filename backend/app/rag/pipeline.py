import hashlib
import uuid

from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.models.knowledge import DocumentChunk, Source, SourceStatus
from app.rag.chunking import split_text
from app.rag.embeddings import get_embedding_model
from app.rag.extract import extract_epub, extract_pdf_text, guess_language
from app.rag.llm import get_llm, load_system_prompt
from app.rag.retrieve import retrieve_chunks
from app.services.ocr import run_ocr
from app.services.palm_cv import extract_palm_features


async def ingest_source_bytes(
    session: AsyncSession,
    source: Source,
    data: bytes,
) -> None:
    source.status = SourceStatus.processing
    await session.commit()

    try:
        lower = source.filename.lower()
        if lower.endswith(".epub"):
            text = extract_epub(data)
        elif lower.endswith(".pdf"):
            text, needs_ocr = extract_pdf_text(data)
            if needs_ocr:
                text = await run_ocr(data)
        else:
            raise ValueError(f"Unsupported format: {source.filename}")

        if not text.strip():
            raise ValueError("No text extracted")

        if not source.language or source.language == "auto":
            source.language = guess_language(text[:5000])

        chunks = split_text(text)
        embedder = get_embedding_model()
        vectors = await embedder.aembed_documents(chunks)

        await session.execute(delete(DocumentChunk).where(DocumentChunk.source_id == source.id))

        for idx, (chunk, vector) in enumerate(zip(chunks, vectors, strict=True)):
            session.add(
                DocumentChunk(
                    source_id=source.id,
                    chunk_index=idx,
                    content=chunk,
                    embedding=vector,
                )
            )

        source.status = SourceStatus.ready
        source.error_message = None
        await session.commit()
    except Exception as exc:
        source.status = SourceStatus.failed
        source.error_message = str(exc)[:2000]
        await session.commit()
        raise


async def rag_answer(session: AsyncSession, user_query: str) -> dict:
    settings = get_settings()
    embedder = get_embedding_model()
    query_vec = await embedder.aembed_query(user_query)
    chunks = await retrieve_chunks(session, query_vec, settings.rag_top_k)

    context_blocks = []
    for ch in chunks:
        title = ch.source.title if ch.source else "unknown"
        context_blocks.append(f"[{title} #{ch.chunk_index}]\n{ch.content}")

    context = "\n\n---\n\n".join(context_blocks) or "(no indexed sources yet)"
    system = load_system_prompt()
    llm = get_llm()
    prompt = f"{system}\n\n" f"Context from CHEIRO library:\n{context}\n\n" f"User request:\n{user_query}"
    response = await llm.ainvoke(prompt)
    text = response.content if hasattr(response, "content") else str(response)

    return {
        "answer": text,
        "sources": [
            {
                "source_id": str(ch.source_id),
                "title": ch.source.title if ch.source else None,
                "author": ch.source.author if ch.source else None,
                "chunk_index": ch.chunk_index,
                "preview": ch.content[:240],
            }
            for ch in chunks
        ],
    }


async def build_palm_report(session: AsyncSession, image_bytes: bytes, locale: str = "ru") -> dict:
    features = await extract_palm_features(image_bytes)
    feature_summary = features.get("summary", "")
    query = (
        f"Palm analysis request. Language: {locale}. "
        f"Observed features (non-diagnostic): {feature_summary}. "
        "Produce: (1) teaser 1-2 sentences, (2) full report structured with headings."
    )
    rag = await rag_answer(session, query)
    answer = rag["answer"]

    # Simple split heuristic for v1; Prompt Studio will replace this later.
    lines = [ln.strip() for ln in answer.split("\n") if ln.strip()]
    teaser = " ".join(lines[:2])[:500] if lines else answer[:280]
    return {"teaser": teaser, "full_report": answer, "features": features, "citations": rag["sources"]}


def compute_content_hash(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def new_source_id() -> uuid.UUID:
    return uuid.uuid4()
