"""End-to-end RAG path against a real PostgreSQL with pgvector.

Runs in CI (service container) and locally with `docker compose up postgres`:
    pytest -m integration
"""

import hashlib
import os
import re
from types import SimpleNamespace

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.database import Base
from app.models.knowledge import EMBEDDING_DIM, Source, SourceStatus
from app.rag import pipeline
from app.rag.retrieve import retrieve_chunks
from tests.test_rag_text import build_epub

pytestmark = pytest.mark.integration

DATABASE_URL = os.environ.get("TEST_DATABASE_URL", "postgresql+asyncpg://cheiro:cheiro@localhost:5432/cheiro")


def embed(text_value: str) -> list[float]:
    """Deterministic bag-of-words hashing embedding: shared words give similar vectors."""
    vector = [0.0] * EMBEDDING_DIM
    for token in re.findall(r"[a-zа-я]+", text_value.lower()):
        bucket = int(hashlib.md5(token.encode(), usedforsecurity=False).hexdigest(), 16) % EMBEDDING_DIM
        vector[bucket] += 1.0
    norm = sum(v * v for v in vector) ** 0.5 or 1.0
    return [v / norm for v in vector]


class FakeEmbeddings:
    async def aembed_documents(self, texts: list[str]) -> list[list[float]]:
        return [embed(t) for t in texts]

    async def aembed_query(self, query: str) -> list[float]:
        return embed(query)


class FakeLLM:
    last_prompt = ""

    async def ainvoke(self, prompt: str):
        FakeLLM.last_prompt = prompt
        return SimpleNamespace(content="Answer grounded in context.")


@pytest.fixture
async def session():
    engine = create_async_engine(DATABASE_URL)
    async with engine.begin() as conn:
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    async with async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)() as db:
        yield db
    await engine.dispose()


@pytest.fixture(autouse=True)
def fake_models(monkeypatch):
    monkeypatch.setattr(pipeline, "get_embedding_model", lambda: FakeEmbeddings())
    monkeypatch.setattr(pipeline, "get_llm", lambda: FakeLLM())


async def ingest_book(db: AsyncSession) -> Source:
    life = "The life line curves around the thumb and describes vitality and energy. " * 40
    heart = "The heart line runs under the fingers and describes emotional intensity. " * 40
    data = build_epub({"Life": life, "Heart": heart})
    source = Source(
        title="Test book", author="A. Author", language="en", filename="book.epub", content_hash="h"
    )
    db.add(source)
    await db.commit()
    await pipeline.ingest_source_bytes(db, source, data)
    return source


async def test_ingest_marks_source_ready_and_stores_vectors(session):
    source = await ingest_book(session)

    assert source.status == SourceStatus.ready
    count = (
        await session.execute(text("SELECT count(*) FROM document_chunks WHERE embedding IS NOT NULL"))
    ).scalar()
    assert count and count > 1


async def test_retrieval_returns_most_relevant_chunk_first(session):
    await ingest_book(session)

    chunks = await retrieve_chunks(session, embed("emotional intensity of the heart line"), top_k=3)

    assert "heart line" in chunks[0].content
    assert chunks[0].source.title == "Test book"


async def test_rag_answer_passes_retrieved_context_and_returns_sources(session):
    await ingest_book(session)

    result = await pipeline.rag_answer(session, "What does the life line say about vitality?")

    assert result["answer"] == "Answer grounded in context."
    assert "Test book" in FakeLLM.last_prompt
    assert "life line" in FakeLLM.last_prompt.lower()
    assert result["sources"]


async def test_failed_ingest_records_error_on_source(session):
    source = Source(title="Broken", language="en", filename="broken.txt", content_hash="x")
    session.add(source)
    await session.commit()

    with pytest.raises(ValueError, match="Unsupported format"):
        await pipeline.ingest_source_bytes(session, source, b"data")

    assert source.status == SourceStatus.failed
    assert "Unsupported format" in (source.error_message or "")
