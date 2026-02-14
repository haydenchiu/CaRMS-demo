"""Program fact table model."""

from typing import Optional, List, TYPE_CHECKING
from datetime import date
from sqlmodel import Field, Relationship, Text, Column

from .base import BaseModel

if TYPE_CHECKING:
    from .university import University
    from .specialty import Specialty
    from .requirement import Requirement
    from .training_site import TrainingSite
    from .selection_criteria import SelectionCriteria


class Program(BaseModel, table=True):
    """Program fact table.
    
    Core fact table containing residency program information.
    """

    __tablename__ = "fact_programs"

    # Foreign keys to dimensions
    university_id: int = Field(foreign_key="dim_universities.id", nullable=False, index=True)
    specialty_id: int = Field(foreign_key="dim_specialties.id", nullable=False, index=True)
    
    # Program identifiers
    program_code: str = Field(nullable=False, index=True, unique=True)
    program_name: str = Field(nullable=False)
    
    # Capacity and status
    quota: Optional[int] = Field(default=None)
    backup_quota: Optional[int] = Field(default=None)
    is_accepting_applications: bool = Field(default=True, nullable=False)
    
    # Program details
    program_type: Optional[str] = Field(default=None, index=True)  # e.g., "R-1", "PGY-1"
    training_duration_years: Optional[int] = Field(default=None)
    language: Optional[str] = Field(default=None, index=True)  # "English", "French", "Bilingual"
    
    # Descriptions (rich text content)
    description: Optional[str] = Field(default=None, sa_column=Column(Text, nullable=True))
    program_overview: Optional[str] = Field(default=None, sa_column=Column(Text, nullable=True))
    curriculum_highlights: Optional[str] = Field(default=None, sa_column=Column(Text, nullable=True))
    
    # Application details
    application_deadline: Optional[date] = Field(default=None)
    interview_start_date: Optional[date] = Field(default=None)
    interview_end_date: Optional[date] = Field(default=None)
    
    # Contact
    program_director: Optional[str] = Field(default=None)
    contact_email: Optional[str] = Field(default=None)
    website: Optional[str] = Field(default=None)
    
    # Metadata from source
    source_file: Optional[str] = Field(default=None)
    carms_year: Optional[int] = Field(default=None, index=True)
    
    # Relationships
    university: "University" = Relationship(back_populates="programs")
    specialty: "Specialty" = Relationship(back_populates="programs")
    requirements: List["Requirement"] = Relationship(back_populates="program")
    training_sites: List["TrainingSite"] = Relationship(back_populates="program")
    selection_criteria: List["SelectionCriteria"] = Relationship(back_populates="program")
    
    class Config:
        json_schema_extra = {
            "example": {
                "program_code": "3507-001",
                "program_name": "Family Medicine - Toronto",
                "university_id": 1,
                "specialty_id": 1,
                "quota": 24,
                "training_duration_years": 2,
                "language": "English",
                "is_accepting_applications": True,
            }
        }
