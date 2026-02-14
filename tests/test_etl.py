"""Tests for ETL pipeline assets."""

import pytest
import pandas as pd
from unittest.mock import Mock, patch

from src.dagster_project.assets.staging import (
    staging_programs,
    staging_universities,
    staging_specialties,
)


@pytest.fixture
def sample_program_master():
    """Sample program master data."""
    return pd.DataFrame({
        'discipline_id': [1, 2, 3],
        'discipline_name': ['Family Medicine', 'Internal Medicine', 'Surgery'],
        'school_id': [100, 101, 100],
        'school_name': ['University of Toronto', 'McGill University', 'University of Toronto'],
        'program_stream_id': ['FM-001', 'IM-002', 'SU-003'],
        'program_stream_name': ['FM Stream 1', 'IM Stream 2', 'Surgery Stream 3'],
        'program_site': ['Toronto', 'Montreal', 'Toronto'],
        'program_name': ['Family Medicine - Toronto', 'Internal Medicine - Montreal', 'General Surgery - Toronto'],
    })


@pytest.fixture
def sample_discipline():
    """Sample discipline data."""
    return pd.DataFrame({
        'discipline_id': [1, 2, 3, 4],
        'discipline': [
            'Family Medicine',
            'Internal Medicine',
            'General Surgery',
            'Surgery - Cardiac'
        ],
    })


class TestStagingPrograms:
    """Tests for staging_programs asset."""
    
    def test_staging_programs_basic_transformation(self, sample_program_master):
        """Test basic transformation of program master data."""
        result = staging_programs(sample_program_master)
        
        assert len(result) == 3
        assert 'program_code' in result.columns
        assert 'program_name' in result.columns
        assert 'specialty_name' in result.columns
        assert 'university_name' in result.columns
        assert 'is_valid' in result.columns
        
    def test_staging_programs_validity_flag(self, sample_program_master):
        """Test that validity flag is set correctly."""
        result = staging_programs(sample_program_master)
        
        # All sample programs should be valid
        assert result['is_valid'].all()
        
    def test_staging_programs_handles_missing_data(self):
        """Test handling of missing data."""
        incomplete_data = pd.DataFrame({
            'discipline_id': [1, 2],
            'discipline_name': ['Family Medicine', None],
            'school_id': [100, None],
            'school_name': ['University of Toronto', ''],
            'program_stream_id': ['FM-001', ''],
            'program_stream_name': ['FM Stream 1', 'Test'],
            'program_site': ['Toronto', 'Montreal'],
            'program_name': ['Test Program', 'Another Program'],
        })
        
        result = staging_programs(incomplete_data)
        
        # Should flag invalid programs
        assert not result['is_valid'].all()
        assert len(result[~result['is_valid']]) > 0


class TestStagingUniversities:
    """Tests for staging_universities asset."""
    
    def test_staging_universities_extraction(self, sample_program_master):
        """Test university extraction from programs."""
        programs = staging_programs(sample_program_master)
        result = staging_universities(programs)
        
        # Should have 2 unique universities
        assert len(result) == 2
        assert 'University of Toronto' in result['university_name'].values
        assert 'McGill University' in result['university_name'].values
        
    def test_staging_universities_province_mapping(self, sample_program_master):
        """Test province mapping logic."""
        programs = staging_programs(sample_program_master)
        result = staging_universities(programs)
        
        # Check that provinces are assigned
        uoft = result[result['university_name'] == 'University of Toronto'].iloc[0]
        assert uoft['province'] == 'Ontario'
        
        mcgill = result[result['university_name'] == 'McGill University'].iloc[0]
        assert mcgill['province'] == 'Quebec'
        
    def test_staging_universities_code_generation(self, sample_program_master):
        """Test university code generation."""
        programs = staging_programs(sample_program_master)
        result = staging_universities(programs)
        
        # Codes should be generated
        assert result['code'].notna().all()
        assert len(result['code'].iloc[0]) > 0


class TestStagingSpecialties:
    """Tests for staging_specialties asset."""
    
    def test_staging_specialties_basic_transformation(self, sample_discipline):
        """Test basic specialty transformation."""
        result = staging_specialties(sample_discipline)
        
        assert len(result) == 4
        assert 'specialty_name' in result.columns
        assert 'code' in result.columns
        assert 'category' in result.columns
        
    def test_staging_specialties_categorization(self, sample_discipline):
        """Test specialty categorization logic."""
        result = staging_specialties(sample_discipline)
        
        # Family Medicine should be Primary Care
        fm = result[result['specialty_name'] == 'Family Medicine'].iloc[0]
        assert fm['category'] == 'Primary Care'
        assert fm['is_primary_care'] == True
        
        # Surgery should be Surgical
        surgery = result[result['specialty_name'] == 'General Surgery'].iloc[0]
        assert surgery['category'] == 'Surgical'
        
    def test_staging_specialties_subspecialty_detection(self, sample_discipline):
        """Test detection of subspecialties."""
        result = staging_specialties(sample_discipline)
        
        # 'Surgery - Cardiac' should be detected as subspecialty
        cardiac = result[result['specialty_name'] == 'Surgery - Cardiac'].iloc[0]
        assert cardiac['is_subspecialty'] == True
        assert cardiac['parent_specialty_name'] == 'Surgery'
        
        # Regular specialties should not be subspecialties
        fm = result[result['specialty_name'] == 'Family Medicine'].iloc[0]
        assert fm['is_subspecialty'] == False


class TestDataQuality:
    """Tests for data quality checks."""
    
    def test_staging_programs_no_duplicates(self, sample_program_master):
        """Test that staging removes or flags duplicate program codes."""
        result = staging_programs(sample_program_master)
        
        # Check for duplicates
        duplicates = result[result.duplicated(subset=['program_code'], keep=False)]
        assert len(duplicates) == 0
        
    def test_staging_programs_required_fields(self, sample_program_master):
        """Test that required fields are populated."""
        result = staging_programs(sample_program_master)
        
        required_fields = ['program_code', 'program_name', 'university_name', 'specialty_name']
        for field in required_fields:
            # Valid programs should have these fields
            valid_programs = result[result['is_valid']]
            assert valid_programs[field].notna().all()
            assert (valid_programs[field] != '').all()
