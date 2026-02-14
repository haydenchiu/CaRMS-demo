"""Tests for SQLModel schemas."""

from datetime import datetime
import pytest
from src.models import University, Specialty, Program


def test_university_creation():
    """Test creating a University instance."""
    university = University(
        name="University of Toronto",
        code="UofT",
        province="Ontario",
        city="Toronto",
        is_francophone=False,
    )
    
    assert university.name == "University of Toronto"
    assert university.code == "UofT"
    assert university.province == "Ontario"
    assert university.is_francophone is False


def test_specialty_creation():
    """Test creating a Specialty instance."""
    specialty = Specialty(
        name="Family Medicine",
        code="FM",
        category="Primary Care",
        training_duration_years=2,
        is_primary_care=True,
    )
    
    assert specialty.name == "Family Medicine"
    assert specialty.code == "FM"
    assert specialty.training_duration_years == 2
    assert specialty.is_primary_care is True


def test_program_creation():
    """Test creating a Program instance."""
    program = Program(
        university_id=1,
        specialty_id=1,
        program_code="3507-001",
        program_name="Family Medicine - Toronto",
        quota=24,
        training_duration_years=2,
        language="English",
        is_accepting_applications=True,
    )
    
    assert program.program_code == "3507-001"
    assert program.quota == 24
    assert program.language == "English"
    assert program.is_accepting_applications is True


def test_base_model_timestamps():
    """Test that timestamp fields are set correctly."""
    university = University(name="Test University")
    
    assert hasattr(university, 'created_at')
    assert hasattr(university, 'updated_at')
    assert university.is_deleted is False


def test_soft_delete():
    """Test soft delete functionality."""
    university = University(name="Test University")
    
    assert university.is_deleted is False
    assert university.deleted_at is None
    
    university.soft_delete()
    
    assert university.is_deleted is True
    assert university.deleted_at is not None
    assert isinstance(university.deleted_at, datetime)
