"""Database connection and utilities."""

from typing import Generator
from contextlib import contextmanager
from sqlmodel import create_engine, Session, SQLModel, text
from loguru import logger

from .config import settings


# Create engine with connection pooling
engine = create_engine(
    settings.database_url,
    echo=settings.debug,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
)


def init_db() -> None:
    """Initialize database by creating all tables."""
    logger.info("Initializing database...")
    SQLModel.metadata.create_all(engine)
    logger.info("Database initialized successfully")


def get_engine():
    """Get the database engine.
    
    Returns the global engine instance for direct access.
    """
    return engine


def drop_db() -> None:
    """Drop all database tables. Use with caution!"""
    logger.warning("Dropping all database tables...")
    SQLModel.metadata.drop_all(engine)
    logger.info("Database tables dropped")


def get_session() -> Generator[Session, None, None]:
    """Get database session for dependency injection.
    
    Usage in FastAPI:
        @app.get("/items")
        def get_items(session: Session = Depends(get_session)):
            ...
    """
    with Session(engine) as session:
        yield session


@contextmanager
def get_db_session() -> Generator[Session, None, None]:
    """Get database session as context manager.
    
    Usage:
        with get_db_session() as session:
            session.execute(...)
    """
    with Session(engine) as session:
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise


def test_connection() -> bool:
    """Test database connection.
    
    Returns:
        True if connection successful, False otherwise.
    """
    try:
        with Session(engine) as session:
            session.exec(text("SELECT 1"))
        logger.info("Database connection successful")
        return True
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return False
