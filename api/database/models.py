from datetime import datetime

from sqlalchemy import UUID, DateTime, Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Job(Base):
    __tablename__ = "jobs"

    job_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True
    )

    benchmark: Mapped[str] = mapped_column(
        String
    )

    status: Mapped[str] = mapped_column(
        String
    )

    retry_count: Mapped[int] = mapped_column(
        Integer
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True)
    )
