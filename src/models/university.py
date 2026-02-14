"""University dimension model."""

from typing import Optional, List, TYPE_CHECKING
from sqlmodel import Field, Relationship

from .base import BaseModel

if TYPE_CHECKING:
    from .program import Program


class University(BaseModel, table=True):
    """University dimension table.
    
    Stores information about Canadian universities offering residency programs.
    """

    __tablename__ = "dim_universities"

    # Core fields
    name: str = Field(nullable=False, index=True, unique=True)
    code: Optional[str] = Field(default=None, index=True)
    province: Optional[str] = Field(default=None, index=True)
    city: Optional[str] = Field(default=None, index=True)
    
    # Contact information
    website: Optional[str] = Field(default=None)
    contact_email: Optional[str] = Field(default=None)
    
    # Additional metadata
    is_francophone: bool = Field(default=False, nullable=False)
    notes: Optional[str] = Field(default=None)
    
    # Relationships
    programs: List["Program"] = Relationship(back_populates="university")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "University of Toronto",
                "code": "UofT",
                "province": "Ontario",
                "city": "Toronto",
                "is_francophone": False,
            }
        }
