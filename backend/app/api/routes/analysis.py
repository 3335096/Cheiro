import base64
import uuid

from fastapi import APIRouter, Depends, Header, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.database import get_db
from app.models.analysis import AnalysisJob, JobStatus
from app.services.telegram_auth import validate_init_data
from app.worker import enqueue_analysis

router = APIRouter(prefix="/api", tags=["analysis"])


class AnalysisCreate(BaseModel):
    image_base64: str = Field(..., description="Base64 image; not persisted to disk")
    locale: str = "ru"


def _telegram_user_id(x_telegram_init_data: str | None) -> str:
    settings = get_settings()
    if settings.debug and not x_telegram_init_data:
        return "dev-user"
    parsed = validate_init_data(x_telegram_init_data or "", settings.telegram_bot_token)
    if not parsed or "user" not in parsed:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Telegram init data")
    user = parsed["user"]
    return str(user.get("id", ""))


@router.post("/analysis")
async def create_analysis(
    body: AnalysisCreate,
    db: AsyncSession = Depends(get_db),
    x_telegram_init_data: str | None = Header(default=None),
) -> dict:
    user_id = _telegram_user_id(x_telegram_init_data)
    try:
        image_bytes = base64.b64decode(body.image_base64, validate=True)
    except Exception as exc:
        raise HTTPException(status_code=400, detail="Invalid image_base64") from exc

    job = AnalysisJob(telegram_user_id=user_id, status=JobStatus.queued)
    db.add(job)
    await db.commit()
    await db.refresh(job)

    from app.worker import store_analysis_payload

    await store_analysis_payload(str(job.id), image_bytes, body.locale)
    await enqueue_analysis(str(job.id))
    return {"job_id": str(job.id), "status": job.status.value}


@router.get("/analysis/{job_id}")
async def get_analysis(
    job_id: str,
    db: AsyncSession = Depends(get_db),
    x_telegram_init_data: str | None = Header(default=None),
) -> dict:
    user_id = _telegram_user_id(x_telegram_init_data)
    try:
        jid = uuid.UUID(job_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail="Job not found") from exc

    result = await db.execute(select(AnalysisJob).where(AnalysisJob.id == jid))
    job = result.scalar_one_or_none()
    if not job or job.telegram_user_id != user_id:
        raise HTTPException(status_code=404, detail="Job not found")

    # The full report is delivered only through the bot; the Mini App never receives it.
    return {
        "job_id": str(job.id),
        "status": job.status.value,
        "teaser": job.teaser,
        "error_message": job.error_message,
    }
