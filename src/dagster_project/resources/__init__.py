"""Dagster resources for database and external services."""

from dagster import ConfigurableResource
from sqlmodel import Session, create_engine
from pydantic import Field


class DatabaseResource(ConfigurableResource):
    """Database resource for Dagster assets.
    
    Provides database connection pooling and session management.
    """

    connection_string: str = Field(
        description="PostgreSQL connection string",
    )
    echo: bool = Field(
        default=False,
        description="Echo SQL statements to logs",
    )

    def get_session(self) -> Session:
        """Get a new database session.
        
        Returns:
            SQLModel Session instance.
        """
        engine = create_engine(
            self.connection_string,
            echo=self.echo,
            pool_pre_ping=True,
        )
        return Session(engine)


# Create resource instance
database_resource = DatabaseResource(
    connection_string="postgresql://carms:carms@localhost:5432/carms",
    echo=False,
)

# Export all resources
resource_defs = {
    "database": database_resource,
}
