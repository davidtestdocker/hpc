# 定義 jobs 資料表與 Python 類別的對應；此處的初始紀錄不會自動追蹤 Kubernetes 最終狀態。
# Python 語法：縮排界定區塊；def 定義函式，冒號後接區塊；型別註記說明預期型別。
from datetime import datetime

from sqlalchemy import UUID, DateTime, Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


# class 定義 Base 類別；括號內是繼承的父類別。
class Base(DeclarativeBase):
    pass


# class 定義 Job 類別；括號內是繼承的父類別。
class Job(Base):
    __tablename__ = "jobs"

    # 宣告資料庫欄位；Mapped[...] 標示 Python 型別，primary_key 表示主鍵。
    job_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True
    )

    # 宣告資料庫欄位；Mapped[...] 標示 Python 型別，primary_key 表示主鍵。
    benchmark: Mapped[str] = mapped_column(
        String
    )

    # 宣告資料庫欄位；Mapped[...] 標示 Python 型別，primary_key 表示主鍵。
    status: Mapped[str] = mapped_column(
        String
    )

    # 宣告資料庫欄位；Mapped[...] 標示 Python 型別，primary_key 表示主鍵。
    retry_count: Mapped[int] = mapped_column(
        Integer
    )

    # 宣告資料庫欄位；Mapped[...] 標示 Python 型別，primary_key 表示主鍵。
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True)
    )
