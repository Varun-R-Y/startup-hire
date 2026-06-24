from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from app.config import settings

# Create synchronous SQLAlchemy engine
engine = create_engine(
    settings.DATABASE_URL,
    echo=False,  # Set to True for SQL log output in development
    pool_pre_ping=True,  # Check connection health before using
)

# Configure session factory
SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    expire_on_commit=False,
)

# Dependency to get sync db session for FastAPI endpoints
def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
