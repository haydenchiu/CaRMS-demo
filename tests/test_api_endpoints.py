"""Enhanced tests for API endpoints."""

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine

from src.api.main import app
from src.models.university import University
from src.models.specialty import Specialty
from src.models.program import Program
from src.models.requirement import Requirement
from src.models.selection_criteria import SelectionCriteria
from src.api.dependencies import get_session


@pytest.fixture(name="test_engine")
def test_engine_fixture():
    """Create a test database engine."""
    engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(engine)
    return engine


@pytest.fixture(name="test_session")
def test_session_fixture(test_engine):
    """Create a test database session."""
    with Session(test_engine) as session:
        yield session


@pytest.fixture(name="test_client")
def test_client_fixture(test_session):
    """Create a test client with dependency override."""
    def get_test_session():
        yield test_session
    
    app.dependency_overrides[get_session] = get_test_session
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture(name="sample_data")
def sample_data_fixture(test_session):
    """Create sample data for testing."""
    # Create university
    university = University(
        name="University of Toronto",
        code="UofT",
        province="Ontario",
        city="Toronto",
        is_francophone=False,
    )
    test_session.add(university)
    test_session.flush()
    
    # Create specialty
    specialty = Specialty(
        name="Family Medicine",
        code="FM",
        category="Primary Care",
        is_primary_care=True,
    )
    test_session.add(specialty)
    test_session.flush()
    
    # Create program
    program = Program(
        program_code="FM-001",
        program_name="Family Medicine - Toronto",
        university_id=university.id,
        specialty_id=specialty.id,
        quota=10,
        is_accepting_applications=True,
        language="English",
        carms_year=2025,
    )
    test_session.add(program)
    test_session.flush()
    
    # Create requirement
    requirement = Requirement(
        program_id=program.id,
        requirement_type="Eligibility",
        requirement_text="Must have completed medical school",
        is_mandatory=True,
    )
    test_session.add(requirement)
    
    # Create selection criteria
    criteria = SelectionCriteria(
        program_id=program.id,
        criterion_type="Academic Performance",
        weight_description="Strong academic record required",
    )
    test_session.add(criteria)
    
    test_session.commit()
    
    return {
        "university": university,
        "specialty": specialty,
        "program": program,
        "requirement": requirement,
        "criteria": criteria,
    }


class TestProgramEndpoints:
    """Tests for program endpoints."""
    
    def test_list_programs(self, test_client, sample_data):
        """Test listing programs."""
        response = test_client.get("/api/v1/programs/")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]["program_code"] == "FM-001"
        
    def test_list_programs_with_filters(self, test_client, sample_data):
        """Test listing programs with filters."""
        # Filter by specialty name
        response = test_client.get("/api/v1/programs/?specialty_name=Family")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        
        # Filter by province
        response = test_client.get("/api/v1/programs/?province=Ontario")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        
        # Filter by non-existent province
        response = test_client.get("/api/v1/programs/?province=Alberta")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 0
        
    def test_get_program_detail(self, test_client, sample_data):
        """Test getting program details."""
        program_id = sample_data["program"].id
        response = test_client.get(f"/api/v1/programs/{program_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["program_code"] == "FM-001"
        assert data["program_name"] == "Family Medicine - Toronto"
        assert "university" in data
        assert "specialty" in data
        
    def test_get_nonexistent_program(self, test_client):
        """Test getting a program that doesn't exist."""
        response = test_client.get("/api/v1/programs/99999")
        assert response.status_code == 404
        
    def test_get_program_requirements(self, test_client, sample_data):
        """Test getting program requirements."""
        program_id = sample_data["program"].id
        response = test_client.get(f"/api/v1/programs/{program_id}/requirements")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]["requirement_type"] == "Eligibility"
        assert data[0]["is_mandatory"] == True
        
    def test_get_program_selection_criteria(self, test_client, sample_data):
        """Test getting program selection criteria."""
        program_id = sample_data["program"].id
        response = test_client.get(f"/api/v1/programs/{program_id}/selection-criteria")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]["criterion_type"] == "Academic Performance"
        
    def test_compare_programs(self, test_client, sample_data):
        """Test comparing programs."""
        program_id = sample_data["program"].id
        
        response = test_client.post(
            "/api/v1/programs/compare",
            json={"program_ids": [program_id, program_id]}  # Compare same program twice for test
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "programs" in data
        assert "comparison_matrix" in data
        assert len(data["programs"]) >= 1


class TestAnalyticsEndpoints:
    """Tests for analytics endpoints."""
    
    def test_get_specialty_statistics(self, test_client, sample_data):
        """Test getting specialty statistics."""
        response = test_client.get("/api/v1/analytics/specialties")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        if len(data) > 0:
            assert "specialty_name" in data[0]
            assert "program_count" in data[0]
            assert "total_quota" in data[0]
            
    def test_get_specialty_statistics_with_filter(self, test_client, sample_data):
        """Test getting specialty statistics with category filter."""
        response = test_client.get("/api/v1/analytics/specialties?category=Primary Care")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        
    def test_get_requirements_summary(self, test_client, sample_data):
        """Test getting requirements summary."""
        response = test_client.get("/api/v1/analytics/requirements/summary")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        
    def test_get_selection_criteria_trends(self, test_client, sample_data):
        """Test getting selection criteria trends."""
        response = test_client.get("/api/v1/analytics/selection-criteria")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        
    def test_get_geographic_distribution(self, test_client, sample_data):
        """Test getting geographic distribution."""
        response = test_client.get("/api/v1/analytics/geographic-distribution")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        
    def test_get_provinces(self, test_client, sample_data):
        """Test getting provinces list."""
        response = test_client.get("/api/v1/analytics/provinces")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        if len(data) > 0:
            assert "province" in data[0]
            assert "program_count" in data[0]


class TestPagination:
    """Tests for pagination."""
    
    def test_list_programs_pagination(self, test_client, sample_data):
        """Test pagination in program listing."""
        # Test with limit
        response = test_client.get("/api/v1/programs/?limit=1")
        assert response.status_code == 200
        data = response.json()
        assert len(data) <= 1
        
        # Test with skip
        response = test_client.get("/api/v1/programs/?skip=0&limit=10")
        assert response.status_code == 200
        
    def test_pagination_validation(self, test_client):
        """Test pagination validation."""
        # Invalid limit (too high)
        response = test_client.get("/api/v1/programs/?limit=1000")
        assert response.status_code == 422  # Validation error
        
        # Invalid skip (negative)
        response = test_client.get("/api/v1/programs/?skip=-1")
        assert response.status_code == 422


class TestErrorHandling:
    """Tests for error handling."""
    
    def test_404_on_nonexistent_resource(self, test_client):
        """Test 404 error on nonexistent resources."""
        response = test_client.get("/api/v1/programs/99999")
        assert response.status_code == 404
        
    def test_422_on_invalid_input(self, test_client):
        """Test 422 error on invalid input."""
        # Invalid program comparison (needs at least 2 programs)
        response = test_client.post(
            "/api/v1/programs/compare",
            json={"program_ids": [1]}  # Only one program
        )
        assert response.status_code == 422
