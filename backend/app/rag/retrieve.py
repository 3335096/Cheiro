from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.knowledge import DocumentChunk


async def retrieve_chunks(
    session: AsyncSession, query_embedding: list[float], top_k: int
) -> list[DocumentChunk]:
    # cosine distance operator <=> in pgvector; order by distance ascending
    stmt = (
        select(DocumentChunk)
        .options(selectinload(DocumentChunk.source))
        .where(DocumentChunk.embedding.isnot(None))
        .order_by(DocumentChunk.embedding.cosine_distance(query_embedding))
        .limit(top_k)
    )
    result = await session.execute(stmt)
    return list(result.scalars().all())
