"""Program requirements dimension model."""

from typing import Optional, TYPE_CHECKING
from sqlmodel import Field, Relationship, Text, Column

from .base import BaseModel

if TYPE_CHECKING:
    from .program import Program


class Requirement(BaseModel, table=True):
    """Program requirements dimension table.
    
    Stores various requirements for residency programs (eligibility, documents, etc.).
    """

    __tablename__ = "dim_requirements"

    # Foreign key
    program_id: int = Field(foreign_key="fact_programs.id", nullable=False, index=True)
    
    # Requirement details
    requirement_type: str = Field(nullable=False, index=True)  # e.g., "eligibility", "documents"
    requirement_category: Optional[str] = Field(default=None)  # e.g., "medical_degree", "licensure"
    
    # Content
    title: Optional[str] = Field(default=None)
    description: str = Field(sa_column=Column(Text, nullable=False))
    
    # Attributes
    is_mandatory: bool = Field(default=True, nullable=False)
    priority: Optional[int] = Field(default=None)  # For ordering
    
    # Relationships
    program: "Program" = Relationship(back_populates="requirements")
    
    class Config:
        json_schema_extra = {
            "example": {
                "program_id": 1,
                "requirement_type": "eligibility",
                "requirement_category": "medical_degree",
                "title": "Medical Degree",
                "description": "Applicants must hold an MD or equivalent degree",
                "is_mandatory": True,
            }
        }
