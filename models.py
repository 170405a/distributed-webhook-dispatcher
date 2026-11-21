
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, Integer, DateTime, func
from sqlalchemy.dialects.postgresql import JSONB


# Base class for all database models
class Base(DeclarativeBase):
    pass


# Main webhook jobs table
class WebhookJob(Base):
    __tablename__ = "webhook_jobs"

    job_id: Mapped[str] = mapped_column(
        String(50), primary_key=True
    )

    event_id: Mapped[str] = mapped_column(
        String(100), nullable=False
    )

    destination_url: Mapped[str] = mapped_column(
        String, nullable=False
    )

    payload: Mapped[dict] = mapped_column(
        JSONB, nullable=False
    )

    status: Mapped[str] = mapped_column(
        String(20), default="pending"
    )

    attempts: Mapped[int] = mapped_column(
        Integer, default=0
    )

    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.current_timestamp()
    )


# Webhook delivery attempts table
class WebhookAttempt(Base):
    __tablename__ = "webhook_attempts"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )

    job_id: Mapped[str] = mapped_column(
        String(50), nullable=False
    )

    event_id: Mapped[str] = mapped_column(
        String(100), nullable=False
    )

    attempt_number: Mapped[int] = mapped_column(
        Integer, nullable=False
    )

    status: Mapped[str] = mapped_column(
        String(20), nullable=False
    )

    http_status_code: Mapped[int | None] = mapped_column(
        Integer, nullable=True
    )

    error_message: Mapped[str | None] = mapped_column(
        String, nullable=True
    )

    attempted_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.current_timestamp()
    )
