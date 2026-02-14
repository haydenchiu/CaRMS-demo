"""Data quality check assets.

These assets validate data quality at various stages of the pipeline.
"""

import pandas as pd
from typing import Dict, Any, List
from sqlmodel import Session, select, func
from dagster import asset, AssetIn, Output, MetadataValue, AssetCheckResult, asset_check
from loguru import logger

from src.models.program import Program
from src.models.university import University
from src.models.specialty import Specialty
from src.utils.database import get_engine


@asset_check(asset="staging_programs")
def check_staging_programs_completeness(staging_programs: pd.DataFrame) -> AssetCheckResult:
    """Check that staging programs have required fields populated."""
    
    # Check for missing critical fields
    required_fields = ['program_code', 'program_name', 'university_name', 'specialty_name']
    
    missing_counts = {}
    for field in required_fields:
        missing = staging_programs[field].isna().sum() + (staging_programs[field] == '').sum()
        missing_counts[field] = int(missing)
    
    total_missing = sum(missing_counts.values())
    total_records = len(staging_programs) * len(required_fields)
    completeness_pct = ((total_records - total_missing) / total_records * 100) if total_records > 0 else 0
    
    passed = completeness_pct >= 95.0  # Require 95% completeness
    
    return AssetCheckResult(
        passed=passed,
        metadata={
            "completeness_percentage": completeness_pct,
            "missing_by_field": MetadataValue.json(missing_counts),
            "total_records": len(staging_programs),
        },
        description=f"Data completeness: {completeness_pct:.1f}% (threshold: 95%)",
    )


@asset_check(asset="staging_programs")
def check_staging_programs_duplicates(staging_programs: pd.DataFrame) -> AssetCheckResult:
    """Check for duplicate program codes in staging data."""
    
    duplicate_codes = staging_programs[staging_programs.duplicated(subset=['program_code'], keep=False)]
    duplicate_count = len(duplicate_codes['program_code'].unique())
    
    passed = duplicate_count == 0
    
    return AssetCheckResult(
        passed=passed,
        metadata={
            "duplicate_count": duplicate_count,
            "total_programs": len(staging_programs),
            "duplicate_codes": MetadataValue.json(duplicate_codes['program_code'].unique().tolist()[:10]) if duplicate_count > 0 else [],
        },
        description=f"Found {duplicate_count} duplicate program codes",
    )


@asset_check(asset="staging_programs")
def check_staging_programs_validity(staging_programs: pd.DataFrame) -> AssetCheckResult:
    """Check that programs pass business rule validation."""
    
    invalid_programs = staging_programs[~staging_programs['is_valid']]
    invalid_count = len(invalid_programs)
    validity_pct = ((len(staging_programs) - invalid_count) / len(staging_programs) * 100) if len(staging_programs) > 0 else 0
    
    passed = validity_pct >= 90.0  # Require 90% valid
    
    return AssetCheckResult(
        passed=passed,
        metadata={
            "validity_percentage": validity_pct,
            "invalid_count": invalid_count,
            "total_programs": len(staging_programs),
        },
        description=f"Validity: {validity_pct:.1f}% ({invalid_count} invalid programs)",
    )


@asset_check(asset="dim_universities")
def check_universities_loaded(dim_universities: int) -> AssetCheckResult:
    """Verify universities were loaded into database."""
    
    engine = get_engine()
    
    with Session(engine) as session:
        count = session.exec(select(func.count(University.id))).one()
    
    passed = count > 0
    
    return AssetCheckResult(
        passed=passed,
        metadata={
            "university_count": count,
        },
        description=f"Loaded {count} universities",
    )


@asset_check(asset="dim_specialties")
def check_specialties_loaded(dim_specialties: int) -> AssetCheckResult:
    """Verify specialties were loaded into database."""
    
    engine = get_engine()
    
    with Session(engine) as session:
        count = session.exec(select(func.count(Specialty.id))).one()
    
    passed = count > 0
    
    return AssetCheckResult(
        passed=passed,
        metadata={
            "specialty_count": count,
        },
        description=f"Loaded {count} specialties",
    )


@asset_check(asset="fact_programs")
def check_programs_referential_integrity(fact_programs: int) -> AssetCheckResult:
    """Check that all programs have valid foreign key references."""
    
    engine = get_engine()
    
    with Session(engine) as session:
        # Check for orphaned programs (invalid university_id)
        orphaned_university = session.exec(
            select(func.count(Program.id))
            .where(
                ~Program.university_id.in_(
                    select(University.id)
                )
            )
        ).one()
        
        # Check for orphaned programs (invalid specialty_id)
        orphaned_specialty = session.exec(
            select(func.count(Program.id))
            .where(
                ~Program.specialty_id.in_(
                    select(Specialty.id)
                )
            )
        ).one()
        
        total_orphaned = orphaned_university + orphaned_specialty
    
    passed = total_orphaned == 0
    
    return AssetCheckResult(
        passed=passed,
        metadata={
            "orphaned_university_refs": orphaned_university,
            "orphaned_specialty_refs": orphaned_specialty,
            "total_orphaned": total_orphaned,
        },
        description=f"Referential integrity: {total_orphaned} orphaned references",
    )


@asset_check(asset="fact_programs")
def check_programs_business_rules(fact_programs: int) -> AssetCheckResult:
    """Validate business rules for programs."""
    
    engine = get_engine()
    violations = []
    
    with Session(engine) as session:
        # Rule 1: Program codes should be unique
        duplicate_codes = session.exec(
            select(Program.program_code, func.count(Program.id))
            .group_by(Program.program_code)
            .having(func.count(Program.id) > 1)
        ).all()
        
        if duplicate_codes:
            violations.append(f"Duplicate program codes: {len(duplicate_codes)}")
        
        # Rule 2: Quota should be positive if set
        invalid_quota = session.exec(
            select(func.count(Program.id))
            .where(Program.quota.is_not(None))
            .where(Program.quota < 1)
        ).one()
        
        if invalid_quota > 0:
            violations.append(f"Invalid quotas (< 1): {invalid_quota}")
        
        # Rule 3: CaRMS year should be reasonable
        invalid_year = session.exec(
            select(func.count(Program.id))
            .where(Program.carms_year.is_not(None))
            .where((Program.carms_year < 2020) | (Program.carms_year > 2030))
        ).one()
        
        if invalid_year > 0:
            violations.append(f"Invalid CaRMS years: {invalid_year}")
    
    passed = len(violations) == 0
    
    return AssetCheckResult(
        passed=passed,
        metadata={
            "violation_count": len(violations),
            "violations": MetadataValue.json(violations),
        },
        description=f"Business rules: {len(violations)} violations",
    )


# Export data quality checks
data_quality_checks = [
    check_staging_programs_completeness,
    check_staging_programs_duplicates,
    check_staging_programs_validity,
    check_universities_loaded,
    check_specialties_loaded,
    check_programs_referential_integrity,
    check_programs_business_rules,
]
