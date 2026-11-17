from fastapi import APIRouter, Depends, File, Form, UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import require_admin
from app.core.database import get_db
from app.models.knowledge import Source
from app.rag.pipeline import compute_content_hash
from app.worker import enqueue_ingest_source

router = APIRouter(prefix="/api/admin", tags=["admin"], dependencies=[Depends(require_admin)])


@router.get("/sources")
async def list_sources(db: AsyncSession = Depends(get_db)) -> list[dict]:
    result = await db.execute(select(Source).order_by(Source.created_at.desc()))
    sources = result.scalars().all()
    return [
        {
            "id": str(s.id),
            "title": s.title,
            "author": s.author,
            "language": s.language,
            "filename": s.filename,
            "status": s.status.value,
            "error_message": s.error_message,
        }
        for s in sources
    ]


@router.post("/sources")
async def upload_source(
    title: str = Form(...),
    author: str | None = Form(None),
    language: str = Form("ru"),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
) -> dict:
    data = await file.read()
    content_hash = compute_content_hash(data)

    existing = await db.execute(select(Source).where(Source.content_hash == content_hash))
    if existing.scalar_one_or_none():
        return {"status": "duplicate", "message": "Source already uploaded"}

    source = Source(
        title=title,
        author=author,
        language=language,
        filename=file.filename or "unknown",
        content_hash=content_hash,
    )
    db.add(source)
    await db.commit()
    await db.refresh(source)

    # Store bytes in Redis temporarily for worker (v1 simple approach)
    from app.worker import store_ingest_payload

    await store_ingest_payload(str(source.id), data)
    await enqueue_ingest_source(str(source.id))
    return {"status": "queued", "source_id": str(source.id)}
