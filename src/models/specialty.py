"""Specialty dimension model."""

from typing import Optional, List, TYPE_CHECKING
from sqlmodel import Field, Relationship

from .base import BaseModel

if TYPE_CHECKING:
    from .program import Program


class Specialty(BaseModel, table=True):
    """Specialty dimension table.
    
    Stores information about medical specialties and disciplines.
    """

    __tablename__ = "dim_specialties"

    # Core fields
    name: str = Field(nullable=False, index=True, unique=True)
    code: Optional[str] = Field(default=None, index=True)
    
    # Hierarchy
    category: Optional[str] = Field(default=None, index=True)  # e.g., "Surgical", "Medical"
    parent_specialty_id: Optional[int] = Field(default=None, foreign_key="dim_specialties.id")
    
    # Metadata
    description: Optional[str] = Field(default=None)
    training_duration_years: Optional[int] = Field(default=None)
    is_primary_care: bool = Field(default=False, nullable=False)
    
    # Relationships
    programs: List["Program"] = Relationship(back_populates="specialty")
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Family Medicine",
                "code": "FM",
                "category": "Primary Care",
                "training_duration_years": 2,
                "is_primary_care": True,
            }
        }
