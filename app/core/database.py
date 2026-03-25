"""
Database connection and session management.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase, scoped_session
from typing import Generator
from contextlib import contextmanager

from app.core.config import get_settings

settings = get_settings()

# Create engine with connection pooling
engine = create_engine(
    settings.DATABASE_URL,
    pool_size=settings.DATABASE_POOL_SIZE,
    max_overflow=settings.DATABASE_MAX_OVERFLOW,
    pool_pre_ping=True,  # Enable connection health checks
    echo=settings.DEBUG,  # Log SQL queries in debug mode
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Scoped session for thread-safe operations
ScopedSession = scoped_session(SessionLocal)


class Base(DeclarativeBase):
    """
    Base class for all SQLAlchemy models.
    Provides common metadata and naming conventions.
    """
    pass


def get_db() -> Generator:
    """
    Dependency for FastAPI endpoints.
    Yields a database session and ensures cleanup.
    
    Usage:
        @app.get("/users")
        def get_users(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def db_session_context():
    """
    Context manager for database sessions outside of FastAPI endpoints.
    
    Usage:
        with db_session_context() as db:
            user = db.query(User).first()
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def init_db() -> None:
    """
    Initialize database tables.
    Call this during application startup or use Alembic for migrations.
    """
    from app.models import Base
    Base.metadata.create_all(bind=engine)


def drop_db() -> None:
    """
    Drop all tables. USE WITH CAUTION.
    """
    from app.models import Base
    Base.metadata.drop_all(bind=engine)
