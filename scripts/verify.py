#!/usr/bin/env python3
"""Verify the installation and configuration."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from loguru import logger


def check_imports() -> bool:
    """Check that all required modules can be imported."""
    logger.info("Checking imports...")
    
    required_modules = [
        "sqlmodel",
        "dagster",
        "fastapi",
        "pandas",
        "pydantic",
        "loguru",
    ]
    
    failed = []
    for module in required_modules:
        try:
            __import__(module)
            logger.success(f"  ✓ {module}")
        except ImportError:
            logger.error(f"  ✗ {module}")
            failed.append(module)
    
    if failed:
        logger.error(f"Failed to import: {', '.join(failed)}")
        return False
    
    return True


def check_models() -> bool:
    """Check that models can be imported."""
    logger.info("Checking models...")
    
    try:
        from src.models import (
            University,
            Specialty,
            Program,
            Requirement,
            TrainingSite,
            SelectionCriteria,
        )
        logger.success("  ✓ All models imported successfully")
        return True
    except Exception as e:
        logger.error(f"  ✗ Failed to import models: {e}")
        return False


def check_config() -> bool:
    """Check configuration."""
    logger.info("Checking configuration...")
    
    try:
        from src.utils.config import settings
        logger.success(f"  ✓ Settings loaded")
        logger.info(f"    - Environment: {settings.environment}")
        logger.info(f"    - Database URL: {settings.database_url[:20]}...")
        logger.info(f"    - Data directory: {settings.data_dir}")
        return True
    except Exception as e:
        logger.error(f"  ✗ Failed to load settings: {e}")
        return False


def check_data_files() -> bool:
    """Check that data files exist."""
    logger.info("Checking data files...")
    
    data_dir = Path("data")
    required_files = [
        "1503_markdown_program_descriptions_v2.json",
        "1503_program_descriptions_x_section.csv",
        "1503_program_master.xlsx",
        "1503_discipline.xlsx",
    ]
    
    missing = []
    for file in required_files:
        file_path = data_dir / file
        if file_path.exists():
            logger.success(f"  ✓ {file}")
        else:
            logger.warning(f"  ✗ {file} (missing)")
            missing.append(file)
    
    if missing:
        logger.warning(f"Missing data files: {', '.join(missing)}")
        logger.info("  Note: Data files are required for ETL pipeline")
    
    return len(missing) == 0


def check_database() -> bool:
    """Check database connection."""
    logger.info("Checking database connection...")
    
    try:
        from src.utils.database import test_connection
        
        if test_connection():
            logger.success("  ✓ Database connection successful")
            return True
        else:
            logger.warning("  ✗ Database connection failed")
            logger.info("    Make sure PostgreSQL is running:")
            logger.info("    cd docker && docker-compose up -d postgres")
            return False
    except Exception as e:
        logger.error(f"  ✗ Database check error: {e}")
        return False


def check_dagster() -> bool:
    """Check Dagster setup."""
    logger.info("Checking Dagster setup...")
    
    try:
        from src.dagster_project import defs
        logger.success("  ✓ Dagster definitions loaded")
        
        # Count assets
        asset_count = len(defs.assets)
        logger.info(f"    - Assets defined: {asset_count}")
        
        return True
    except Exception as e:
        logger.error(f"  ✗ Failed to load Dagster definitions: {e}")
        return False


def check_api() -> bool:
    """Check API setup."""
    logger.info("Checking API setup...")
    
    try:
        from src.api import app
        logger.success("  ✓ FastAPI app loaded")
        
        # Count routes
        route_count = len(app.routes)
        logger.info(f"    - Routes defined: {route_count}")
        
        return True
    except Exception as e:
        logger.error(f"  ✗ Failed to load API: {e}")
        return False


def main() -> None:
    """Run all verification checks."""
    logger.info("=" * 50)
    logger.info("CaRMS Platform - Installation Verification")
    logger.info("=" * 50)
    logger.info("")
    
    checks = [
        ("Imports", check_imports),
        ("Models", check_models),
        ("Configuration", check_config),
        ("Data Files", check_data_files),
        ("Database", check_database),
        ("Dagster", check_dagster),
        ("API", check_api),
    ]
    
    results = {}
    for name, check_func in checks:
        try:
            results[name] = check_func()
        except Exception as e:
            logger.error(f"Check '{name}' failed with error: {e}")
            results[name] = False
        logger.info("")
    
    # Summary
    logger.info("=" * 50)
    logger.info("Summary")
    logger.info("=" * 50)
    
    passed = sum(results.values())
    total = len(results)
    
    for name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        logger.info(f"{status}: {name}")
    
    logger.info("")
    logger.info(f"Passed: {passed}/{total}")
    
    if passed == total:
        logger.success("🎉 All checks passed! Installation is ready.")
        logger.info("")
        logger.info("Next steps:")
        logger.info("1. Start services: cd docker && docker-compose up -d")
        logger.info("2. Initialize DB: python scripts/init_db.py")
        logger.info("3. Open Dagster: http://localhost:3000")
        logger.info("4. Open API docs: http://localhost:8000/docs")
    else:
        logger.warning("⚠️  Some checks failed. Please review the errors above.")
        
        if not results.get("Database"):
            logger.info("")
            logger.info("To start the database:")
            logger.info("  cd docker && docker-compose up -d postgres")


if __name__ == "__main__":
    main()
