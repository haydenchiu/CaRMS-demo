"""Database initialization script.

Run this script to create all database tables.
"""

from loguru import logger
from src.utils.database import init_db, test_connection

# Import all models to register them with SQLModel
from src.models import (
    University,
    Specialty,
    Program,
    Requirement,
    TrainingSite,
    SelectionCriteria,
)


def main() -> None:
    """Initialize the database."""
    logger.info("CaRMS Database Initialization")
    logger.info("=" * 50)

    # Test connection first
    if not test_connection():
        logger.error("Cannot connect to database. Please check your DATABASE_URL.")
        return

    # Initialize tables
    try:
        init_db()
        logger.success("Database initialization completed successfully!")
        logger.info(f"Created tables:")
        logger.info("  - dim_universities")
        logger.info("  - dim_specialties")
        logger.info("  - dim_requirements")
        logger.info("  - dim_training_sites")
        logger.info("  - dim_selection_criteria")
        logger.info("  - fact_programs")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise


if __name__ == "__main__":
    main()
