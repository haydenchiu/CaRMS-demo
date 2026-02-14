"""Selection criteria dimension model."""

from typing import Optional, TYPE_CHECKING
from sqlmodel import Field, Relationship, Text, Column

from .base import BaseModel

if TYPE_CHECKING:
    from .program import Program


class SelectionCriteria(BaseModel, table=True):
    """Selection criteria dimension table.
    
    Stores how programs evaluate and select candidates.
    """

    __tablename__ = "dim_selection_criteria"

    # Foreign key
    program_id: int = Field(foreign_key="fact_programs.id", nullable=False, index=True)
    
    # Criteria details
    criteria_type: str = Field(nullable=False, index=True)  # e.g., "academic", "clinical", "research"
    criteria_name: str = Field(nullable=False)
    
    # Content
    description: str = Field(sa_column=Column(Text, nullable=False))
    
    # Weighting
    weight_percentage: Optional[float] = Field(default=None)  # If provided
    priority: Optional[int] = Field(default=None)  # For ordering
    
    # Relationships
    program: "Program" = Relationship(back_populates="selection_criteria")
    
    class Config:
        json_schema_extra = {
            "example": {
                "program_id": 1,
                "criteria_type": "academic",
                "criteria_name": "Medical School Performance",
                "description": "Strong academic record with emphasis on core clerkship rotations",
                "weight_percentage": 40.0,
            }
        }
