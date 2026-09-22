# 從環境變數組合 PostgreSQL 連線網址，建立 SQLAlchemy 連線引擎。
# Python 語法：縮排界定區塊；def 定義函式，冒號後接區塊；型別註記說明預期型別。
import os

from sqlalchemy import create_engine

# 讀取環境變數，未設定時使用第二個引數的預設值。
POSTGRES_HOST = os.getenv(
    "POSTGRES_HOST",
    "postgres-service"
)

# 讀取環境變數，未設定時使用第二個引數的預設值。
POSTGRES_PORT = os.getenv(
    "POSTGRES_PORT",
    "5432"
)

# 讀取環境變數，未設定時使用第二個引數的預設值。
POSTGRES_DB = os.getenv(
    "POSTGRES_DB",
    "hpc_platform"
)

# 讀取環境變數，未設定時使用第二個引數的預設值。
POSTGRES_USER = os.getenv(
    "POSTGRES_USER",
    "hpc"
)

# 讀取環境變數，未設定時使用第二個引數的預設值。
POSTGRES_PASSWORD = os.getenv(
    "POSTGRES_PASSWORD",
    "hpc_password"
)

DATABASE_URL = (
    "postgresql+psycopg2://"
    f"{POSTGRES_USER}:{POSTGRES_PASSWORD}"
    f"@{POSTGRES_HOST}:{POSTGRES_PORT}"
    f"/{POSTGRES_DB}"
)

# 建立 SQLAlchemy Engine；實際連線通常在第一次資料庫操作時取得。
# pool_pre_ping 檢查池中舊連線；限制連線／SQL 等待時間，讓背景 worker 能返回重試。
engine = create_engine(
    DATABASE_URL, pool_pre_ping=True, pool_timeout=10,
    connect_args={'connect_timeout': 5, 'options': '-c statement_timeout=15000'},
)
