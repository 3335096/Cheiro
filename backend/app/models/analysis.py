import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class JobStatus(str, enum.Enum):
    queued = "queued"
    recognizing = "recognizing"
    searching = "searching"
    generating = "generating"
    done = "done"
    failed = "failed"


class AnalysisJob(Base):
    __tablename__ = "analysis_jobs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    telegram_user_id: Mapped[str] = mapped_column(String(64), index=True)
    status: Mapped[JobStatus] = mapped_column(Enum(JobStatus, name="job_status"), default=JobStatus.queued)
    palm_features_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    teaser: Mapped[str | None] = mapped_column(Text, nullable=True)
    full_report: Mapped[str | None] = mapped_column(Text, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )