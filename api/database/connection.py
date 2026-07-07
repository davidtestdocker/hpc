from sqlalchemy import create_engine

DATABASE_URL = (
    "postgresql+psycopg2://"
    "hpc:hpc_password@postgres-service:5432/hpc_platform"
)
engine = create_engine(
    DATABASE_URL
)
