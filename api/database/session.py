# 建立資料庫 Session 工廠；每次呼叫 SessionLocal() 都會建立一個操作單位。
# Python 語法：縮排界定區塊；def 定義函式，冒號後接區塊；型別註記說明預期型別。
from sqlalchemy.orm import sessionmaker

from api.database.connection import engine

# 建立 Session 工廠；autoflush=False 停用查詢前自動 flush，交易由程式控制。
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False
)
