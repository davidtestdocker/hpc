from sqlalchemy import String
from sqlalchemy import UUID
from sqlalchemy import Integer
from sqlalchemy import DateTime
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from datetime import datetime


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
