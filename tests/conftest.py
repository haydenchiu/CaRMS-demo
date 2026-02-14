"""Pytest configuration and shared fixtures."""

import pytest
from sqlmodel import Session, create_engine, SQLModel
from fastapi.testclient import TestClient

from src.api.main import app
from src.utils.config import settings


@pytest.fixture(name="session")
def session_fixture():
    """Create a test database session."""
    # Use in-memory SQLite for testing
    engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(engine)
    
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture():
    """Create a test client for the FastAPI app."""
    return TestClient(app)
