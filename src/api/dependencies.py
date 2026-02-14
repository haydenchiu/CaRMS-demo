"""Shared dependencies for FastAPI routes."""

from typing import Generator
from sqlmodel import Session
from src.utils.database import get_engine


def get_session() -> Generator[Session, None, None]:
    """Dependency that provides a database session.
    
    Yields a session and ensures it's closed after the request.
    """
    engine = get_engine()
    with Session(engine) as session:
        yield session
