import os

from sqlalchemy import create_engine

POSTGRES_HOST = os.getenv(
    "POSTGRES_HOST",
    "postgres-service"
)

POSTGRES_PORT = os.getenv(
    "POSTGRES_PORT",
    "5432"
)

POSTGRES_DB = os.getenv(
    "POSTGRES_DB",
    "hpc_platform"
)

POSTGRES_USER = os.getenv(
    "POSTGRES_USER",
    "hpc"
)

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

engine = create_engine(DATABASE_URL)
