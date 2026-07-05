from sqlalchemy.orm import sessionmaker

from api.database.connection import engine

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False
)
