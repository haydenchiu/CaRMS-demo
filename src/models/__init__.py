"""SQLModel database schemas."""

from .base import BaseModel, TimestampMixin
from .university import University
from .specialty import Specialty
from .program import Program
from .requirement import Requirement
from .training_site import TrainingSite
from .selection_criteria import SelectionCriteria

__all__ = [
    "BaseModel",
    "TimestampMixin",
    "University",
    "Specialty",
    "Program",
    "Requirement",
    "TrainingSite",
    "SelectionCriteria",
]
