"""Pydantic schemas for API request and response models."""

from typing import Optional, List
from datetime import date, datetime
from pydantic import BaseModel, Field, ConfigDict


# Base schemas
class TimestampSchema(BaseModel):
    """Base schema with timestamps."""
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# University schemas
class UniversityBase(BaseModel):
    """Base university schema."""
    name: str
    code: Optional[str] = None
    province: Optional[str] = None
    city: Optional[str] = None
    is_francophone: bool = False


class UniversityResponse(UniversityBase, TimestampSchema):
    """University response schema."""
    id: int
    
    model_config = ConfigDict(from_attributes=True)


# Specialty schemas
class SpecialtyBase(BaseModel):
    """Base specialty schema."""
    name: str
    code: Optional[str] = None
    category: Optional[str] = None
    is_primary_care: bool = False


class SpecialtyResponse(SpecialtyBase, TimestampSchema):
    """Specialty response schema."""
    id: int
    parent_specialty_id: Optional[int] = None
    
    model_config = ConfigDict(from_attributes=True)


# Program schemas
class ProgramBase(BaseModel):
    """Base program schema."""
    program_code: str
    program_name: str
    quota: Optional[int] = None
    is_accepting_applications: bool = True


class ProgramListResponse(ProgramBase, TimestampSchema):
    """Program list response (summary)."""
    id: int
    university_id: int
    specialty_id: int
    program_type: Optional[str] = None
    language: Optional[str] = None
    carms_year: Optional[int] = None
    
    model_config = ConfigDict(from_attributes=True)


class ProgramDetailResponse(ProgramListResponse):
    """Program detail response (full information)."""
    backup_quota: Optional[int] = None
    training_duration_years: Optional[int] = None
    description: Optional[str] = None
    program_overview: Optional[str] = None
    curriculum_highlights: Optional[str] = None
    application_deadline: Optional[date] = None
    interview_start_date: Optional[date] = None
    interview_end_date: Optional[date] = None
    program_director: Optional[str] = None
    contact_email: Optional[str] = None
    website: Optional[str] = None
    source_file: Optional[str] = None
    
    # Related data
    university: Optional[UniversityResponse] = None
    specialty: Optional[SpecialtyResponse] = None


# Requirement schemas
class RequirementResponse(BaseModel):
    """Requirement response schema."""
    id: int
    program_id: int
    requirement_type: str
    requirement_text: str
    is_mandatory: bool = False
    
    model_config = ConfigDict(from_attributes=True)


# Selection criteria schemas
class SelectionCriteriaResponse(BaseModel):
    """Selection criteria response schema."""
    id: int
    program_id: int
    criterion_type: str
    weight_description: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)


# Training site schemas
class TrainingSiteResponse(BaseModel):
    """Training site response schema."""
    id: int
    program_id: int
    site_name: str
    site_type: Optional[str] = None
    city: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)


# Program filters
class ProgramFilters(BaseModel):
    """Filters for program queries."""
    specialty_id: Optional[int] = Field(None, description="Filter by specialty ID")
    specialty_name: Optional[str] = Field(None, description="Filter by specialty name (partial match)")
    university_id: Optional[int] = Field(None, description="Filter by university ID")
    university_name: Optional[str] = Field(None, description="Filter by university name (partial match)")
    province: Optional[str] = Field(None, description="Filter by province")
    language: Optional[str] = Field(None, description="Filter by language")
    is_accepting_applications: Optional[bool] = Field(None, description="Filter by application status")
    min_quota: Optional[int] = Field(None, description="Minimum quota")
    max_quota: Optional[int] = Field(None, description="Maximum quota")
    skip: int = Field(0, ge=0, description="Number of records to skip")
    limit: int = Field(100, ge=1, le=500, description="Maximum number of records to return")


# Program comparison request
class ProgramCompareRequest(BaseModel):
    """Request to compare multiple programs."""
    program_ids: List[int] = Field(..., min_length=2, max_length=10, description="List of program IDs to compare")


# Program comparison response
class ProgramComparisonResponse(BaseModel):
    """Response for program comparison."""
    programs: List[ProgramDetailResponse]
    comparison_matrix: dict = Field(..., description="Side-by-side comparison data")


# Analytics schemas
class SpecialtyStatsResponse(BaseModel):
    """Specialty statistics response."""
    specialty_id: int
    specialty_name: str
    specialty_category: Optional[str] = None
    program_count: int
    total_quota: int
    avg_quota_per_program: float
    universities_offering: int


class RequirementSummaryResponse(BaseModel):
    """Requirements summary by specialty."""
    specialty_name: str
    requirement_type: str
    requirement_count: int
    mandatory_count: int
    optional_count: int


class SelectionCriteriaTrendResponse(BaseModel):
    """Selection criteria trends."""
    specialty_category: str
    criterion_type: str
    mention_count: int
    program_count: int
    avg_mentions_per_program: float


class GeographicDistributionResponse(BaseModel):
    """Geographic distribution of programs."""
    province: str
    city: Optional[str] = None
    specialty_category: str
    program_count: int
    total_quota: int


# Error response
class ErrorResponse(BaseModel):
    """Standard error response."""
    error: str
    detail: Optional[str] = None
    status_code: int
