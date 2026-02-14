"""Tests for FastAPI endpoints."""

import pytest
from fastapi.testclient import TestClient


def test_root_endpoint(client):
    """Test the root endpoint."""
    response = client.get("/")
    
    assert response.status_code == 200
    data = response.json()
    
    assert "name" in data
    assert "version" in data
    assert data["name"] == "CaRMS Residency Program Data Platform"


def test_health_check(client):
    """Test the health check endpoint."""
    response = client.get("/health")
    
    assert response.status_code == 200
    data = response.json()
    
    assert "status" in data
    assert "database" in data
    assert "environment" in data
