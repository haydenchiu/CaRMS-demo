"""Training site dimension model."""

from typing import Optional, TYPE_CHECKING
from sqlmodel import Field, Relationship, Text, Column

from .base import BaseModel

if TYPE_CHECKING:
    from .program import Program


class TrainingSite(BaseModel, table=True):
    """Training site dimension table.
    
    Stores information about clinical training locations for programs.
    """

    __tablename__ = "dim_training_sites"

    # Foreign key
    program_id: int = Field(foreign_key="fact_programs.id", nullable=False, index=True)
    
    # Site information
    site_name: str = Field(nullable=False)
    site_type: Optional[str] = Field(default=None, index=True)  # e.g., "hospital", "clinic", "community"
    
    # Location
    city: Optional[str] = Field(default=None, index=True)
    province: Optional[str] = Field(default=None, index=True)
    address: Optional[str] = Field(default=None)
    
    # Details
    description: Optional[str] = Field(default=None, sa_column=Column(Text, nullable=True))
    rotation_duration_weeks: Optional[int] = Field(default=None)
    is_primary_site: bool = Field(default=False, nullable=False)
    
    # Relationships
    program: "Program" = Relationship(back_populates="training_sites")
    
    class Config:
        json_schema_extra = {
            "example": {
                "program_id": 1,
                "site_name": "Toronto General Hospital",
                "site_type": "hospital",
                "city": "Toronto",
                "province": "Ontario",
                "is_primary_site": True,
            }
        }
