from typing import Any, ClassVar

import redis.asyncio as redis
from arq import create_pool
from arq.connections import RedisSettings
from sqlalchemy import select

from app.core.config import get_settings
from app.core.database import SessionLocal, engine
from app.models.analysis import AnalysisJob, JobStatus
from app.models.knowledge import Source
from app.rag.pipeline import build_palm_report, ingest_source_bytes

INGEST_PREFIX = "cheiro:ingest:"
ANALYSIS_PREFIX = "cheiro:analysis:"


def _redis_settings() -> RedisSettings:
    settings = get_settings()
    return RedisSettings.from_dsn(settings.redis_url)


async def _redis() -> redis.Redis:
    return redis.from_url(get_settings().redis_url, decode_responses=False)


async def store_ingest_payload(source_id: str, data: bytes) -> None:
    r = await _redis()
    try:
        await r.set(f"{INGEST_PREFIX}{source_id}", data, ex=3600)
    finally:
        await r.aclose()


async def store_analysis_payload(job_id: str, image_bytes: bytes, locale: str) -> None:
    r = await _redis()
    try:
        payload = f"{locale}|".encode() + image_bytes
        await r.set(f"{ANALYSIS_PREFIX}{job_id}", payload, ex=1800)
    finally:
        await r.aclose()


async def enqueue_ingest_source(source_id: str) -> None:
    redis_pool = await create_pool(_redis_settings())
    try:
        await redis_pool.enqueue_job("ingest_source_job", source_id)
    finally:
        await redis_pool.aclose()


async def enqueue_analysis(job_id: str) -> None:
    redis_pool = await create_pool(_redis_settings())
    try:
        await redis_pool.enqueue_job("analysis_job", job_id)
    finally:
        await redis_pool.aclose()


async def ingest_source_job(ctx: dict[str, Any], source_id: str) -> None:
    del ctx
    r = await _redis()
    try:
        data = await r.get(f"{INGEST_PREFIX}{source_id}")
        if not data:
            raise RuntimeError("Ingest payload missing in Redis")
        await r.delete(f"{INGEST_PREFIX}{source_id}")

        import uuid

        async with SessionLocal() as session:
            sid = uuid.UUID(source_id)
            result = await session.execute(select(Source).where(Source.id == sid))
            source = result.scalar_one_or_none()
            if not source:
                raise RuntimeError("Source not found")
            await ingest_source_bytes(session, source, data)
    finally:
        await r.aclose()


async def analysis_job(ctx: dict[str, Any], job_id: str) -> None:
    del ctx
    r = await _redis()
    try:
        raw = await r.get(f"{ANALYSIS_PREFIX}{job_id}")
        if not raw:
            raise RuntimeError("Analysis payload missing")
        await r.delete(f"{ANALYSIS_PREFIX}{job_id}")

        locale, image_bytes = _split_analysis_payload(raw)

        import uuid

        async with SessionLocal() as session:
            jid = uuid.UUID(job_id)
            result = await session.execute(select(AnalysisJob).where(AnalysisJob.id == jid))
            job = result.scalar_one_or_none()
            if not job:
                return

            for status in (JobStatus.recognizing, JobStatus.searching, JobStatus.generating):
                job.status = status
                await session.commit()

            try:
                report = await build_palm_report(session, image_bytes, locale=locale)
                job.palm_features_json = str(report.get("features"))
                job.teaser = report["teaser"]
                job.full_report = report["full_report"]
                job.status = JobStatus.done
                from app.services.telegram_bot import send_message

                if job.full_report:
                    await send_message(job.telegram_user_id, job.full_report)
            except Exception as exc:
                job.status = JobStatus.failed
                job.error_message = str(exc)[:2000]
            await session.commit()
    finally:
        await r.aclose()


def _split_analysis_payload(raw: bytes) -> tuple[str, bytes]:
    if b"|" in raw:
        head, image = raw.split(b"|", 1)
        return head.decode(), image
    return "ru", raw


async def startup(ctx: dict[str, Any]) -> None:
    del ctx
    from sqlalchemy import text

    from app.core.database import Base

    async with engine.begin() as conn:
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        await conn.run_sync(Base.metadata.create_all)


class WorkerSettings:
    functions: ClassVar[list] = [ingest_source_job, analysis_job]
    on_startup = startup
    redis_settings = _redis_settings()
