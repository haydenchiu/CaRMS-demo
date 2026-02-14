"""Base model classes with common functionality."""

from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel


class TimestampMixin(SQLModel):
    """Mixin for created_at and updated_at timestamps."""

    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        sa_column_kwargs={"onupdate": datetime.utcnow},
    )


class BaseModel(TimestampMixin):
    """Base model with ID, timestamps, and soft delete."""

    id: Optional[int] = Field(default=None, primary_key=True)
    is_deleted: bool = Field(default=False, nullable=False, index=True)
    deleted_at: Optional[datetime] = Field(default=None)

    def soft_delete(self) -> None:
        """Soft delete the record."""
        self.is_deleted = True
        self.deleted_at = datetime.utcnow()
