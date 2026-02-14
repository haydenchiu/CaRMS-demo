"""Serving layer assets.

These assets populate the final data warehouse tables (dimensions and facts).
"""

import pandas as pd
from typing import Dict, Any
from sqlmodel import Session, select
from dagster import asset, AssetIn, Output, MetadataValue, get_dagster_logger
from loguru import logger

from src.models.university import University
from src.models.specialty import Specialty
from src.models.program import Program
from src.models.requirement import Requirement
from src.models.selection_criteria import SelectionCriteria
from src.models.training_site import TrainingSite
from src.utils.database import get_engine


@asset(
    ins={"staging_universities": AssetIn()},
    group_name="serving",
    description="Load universities into dimension table",
)
def dim_universities(staging_universities: pd.DataFrame) -> Output[int]:
    """Populate the universities dimension table.
    
    Returns the number of universities loaded.
    """
    logger.info("Loading universities into dimension table")
    
    engine = get_engine()
    inserted_count = 0
    updated_count = 0
    
    with Session(engine) as session:
        for _, row in staging_universities.iterrows():
            # Check if university already exists
            stmt = select(University).where(University.name == row['university_name'])
            existing = session.exec(stmt).first()
            
            if existing:
                # Update existing record
                existing.code = row.get('code')
                existing.province = row.get('province')
                existing.is_francophone = row.get('is_francophone', False)
                updated_count += 1
            else:
                # Create new record
                university = University(
                    name=row['university_name'],
                    code=row.get('code'),
                    province=row.get('province'),
                    is_francophone=row.get('is_francophone', False),
                )
                session.add(university)
                inserted_count += 1
        
        session.commit()
    
    total = inserted_count + updated_count
    logger.info(f"Loaded {total} universities ({inserted_count} new, {updated_count} updated)")
    
    return Output(
        total,
        metadata={
            "inserted": inserted_count,
            "updated": updated_count,
            "total": total,
        }
    )


@asset(
    ins={"staging_specialties": AssetIn()},
    group_name="serving",
    description="Load specialties into dimension table",
)
def dim_specialties(staging_specialties: pd.DataFrame) -> Output[int]:
    """Populate the specialties dimension table.
    
    Handles parent-child relationships for subspecialties.
    """
    logger.info("Loading specialties into dimension table")
    
    engine = get_engine()
    inserted_count = 0
    updated_count = 0
    
    with Session(engine) as session:
        # First pass: create all specialties
        specialty_map = {}  # Map name to ID for parent lookup
        
        for _, row in staging_specialties.iterrows():
            stmt = select(Specialty).where(Specialty.name == row['specialty_name'])
            existing = session.exec(stmt).first()
            
            if existing:
                existing.code = row.get('code')
                existing.category = row.get('category')
                existing.is_primary_care = row.get('is_primary_care', False)
                specialty_map[row['specialty_name']] = existing.id
                updated_count += 1
            else:
                specialty = Specialty(
                    name=row['specialty_name'],
                    code=row.get('code'),
                    category=row.get('category'),
                    is_primary_care=row.get('is_primary_care', False),
                )
                session.add(specialty)
                session.flush()  # Get ID
                specialty_map[row['specialty_name']] = specialty.id
                inserted_count += 1
        
        session.commit()
        
        # Second pass: link parent specialties for subspecialties
        for _, row in staging_specialties[staging_specialties['is_subspecialty']].iterrows():
            parent_name = row.get('parent_specialty_name')
            if parent_name and parent_name in specialty_map:
                stmt = select(Specialty).where(Specialty.name == row['specialty_name'])
                specialty = session.exec(stmt).first()
                if specialty:
                    specialty.parent_specialty_id = specialty_map[parent_name]
        
        session.commit()
    
    total = inserted_count + updated_count
    logger.info(f"Loaded {total} specialties ({inserted_count} new, {updated_count} updated)")
    
    return Output(
        total,
        metadata={
            "inserted": inserted_count,
            "updated": updated_count,
            "total": total,
        }
    )


@asset(
    ins={
        "staging_programs": AssetIn(),
        "staging_program_descriptions": AssetIn(),
        "dim_universities": AssetIn(),
        "dim_specialties": AssetIn(),
    },
    group_name="serving",
    description="Load programs into fact table",
)
def fact_programs(
    staging_programs: pd.DataFrame,
    staging_program_descriptions: pd.DataFrame,
    dim_universities: int,
    dim_specialties: int,
) -> Output[int]:
    """Populate the programs fact table.
    
    Links to university and specialty dimensions.
    """
    logger.info("Loading programs into fact table")
    
    engine = get_engine()
    inserted_count = 0
    updated_count = 0
    skipped_count = 0
    
    # Create lookup dictionaries for faster joins
    university_lookup = {}
    specialty_lookup = {}
    
    with Session(engine) as session:
        # Build lookups
        universities = session.exec(select(University)).all()
        for uni in universities:
            university_lookup[uni.name] = uni.id
        
        specialties = session.exec(select(Specialty)).all()
        for spec in specialties:
            specialty_lookup[spec.name] = spec.id
        
        # Merge program data with descriptions
        # Note: We'll need to match by some common field - for now use index position
        # In production, we'd have a proper join key
        
        for idx, prog_row in staging_programs[staging_programs['is_valid']].iterrows():
            university_id = university_lookup.get(prog_row['university_name'])
            specialty_id = specialty_lookup.get(prog_row['specialty_name'])
            
            if not university_id or not specialty_id:
                skipped_count += 1
                logger.warning(f"Skipping program {prog_row['program_code']}: missing university or specialty")
                continue
            
            # Try to find matching description (by position for now)
            description_row = None
            if idx < len(staging_program_descriptions):
                description_row = staging_program_descriptions.iloc[idx]
            
            # Check if program exists
            stmt = select(Program).where(Program.program_code == prog_row['program_code'])
            existing = session.exec(stmt).first()
            
            if existing:
                # Update existing
                existing.program_name = prog_row['program_name']
                existing.university_id = university_id
                existing.specialty_id = specialty_id
                existing.carms_year = prog_row.get('carms_year', 2025)
                
                if description_row is not None:
                    existing.description = description_row.get('full_content', '')[:10000]
                    existing.program_overview = description_row.get('program_overview', '')[:5000]
                    existing.curriculum_highlights = description_row.get('curriculum', '')[:5000]
                
                updated_count += 1
            else:
                # Create new
                program = Program(
                    program_code=prog_row['program_code'],
                    program_name=prog_row['program_name'],
                    university_id=university_id,
                    specialty_id=specialty_id,
                    carms_year=prog_row.get('carms_year', 2025),
                    source_file=prog_row.get('source_file'),
                    is_accepting_applications=True,
                )
                
                if description_row is not None:
                    program.description = description_row.get('full_content', '')[:10000]
                    program.program_overview = description_row.get('program_overview', '')[:5000]
                    program.curriculum_highlights = description_row.get('curriculum', '')[:5000]
                
                session.add(program)
                inserted_count += 1
        
        session.commit()
    
    total = inserted_count + updated_count
    logger.info(f"Loaded {total} programs ({inserted_count} new, {updated_count} updated, {skipped_count} skipped)")
    
    return Output(
        total,
        metadata={
            "inserted": inserted_count,
            "updated": updated_count,
            "skipped": skipped_count,
            "total": total,
        }
    )


@asset(
    ins={
        "staging_requirements": AssetIn(),
        "fact_programs": AssetIn(),
    },
    group_name="serving",
    description="Load program requirements",
)
def dim_requirements(
    staging_requirements: pd.DataFrame,
    fact_programs: int,
) -> Output[int]:
    """Populate requirements dimension linked to programs."""
    logger.info("Loading program requirements")
    
    engine = get_engine()
    inserted_count = 0
    
    # Build program lookup by CARMS ID
    # Note: In production, we'd have proper mapping. For now, use program codes
    program_lookup = {}
    
    with Session(engine) as session:
        programs = session.exec(select(Program)).all()
        for prog in programs:
            # Extract CARMS ID from code if possible
            program_lookup[str(prog.program_code)] = prog.id
        
        for _, row in staging_requirements.iterrows():
            # Try to match program
            carms_id = str(row['carms_id'])
            
            # Find matching program (this is a simplification)
            program_id = None
            for code, pid in program_lookup.items():
                if code in carms_id or carms_id in code:
                    program_id = pid
                    break
            
            if not program_id:
                continue
            
            # Create requirement
            requirement = Requirement(
                program_id=program_id,
                requirement_type=row['requirement_type'],
                requirement_text=row['requirement_text'],
                is_mandatory=row.get('is_mandatory', False),
            )
            session.add(requirement)
            inserted_count += 1
        
        session.commit()
    
    logger.info(f"Loaded {inserted_count} requirements")
    
    return Output(
        inserted_count,
        metadata={
            "inserted": inserted_count,
        }
    )


@asset(
    ins={
        "staging_selection_criteria": AssetIn(),
        "fact_programs": AssetIn(),
    },
    group_name="serving",
    description="Load selection criteria",
)
def dim_selection_criteria(
    staging_selection_criteria: pd.DataFrame,
    fact_programs: int,
) -> Output[int]:
    """Populate selection criteria dimension."""
    logger.info("Loading selection criteria")
    
    engine = get_engine()
    inserted_count = 0
    
    program_lookup = {}
    
    with Session(engine) as session:
        programs = session.exec(select(Program)).all()
        for prog in programs:
            program_lookup[str(prog.program_code)] = prog.id
        
        for _, row in staging_selection_criteria.iterrows():
            carms_id = str(row['carms_id'])
            
            # Find matching program
            program_id = None
            for code, pid in program_lookup.items():
                if code in carms_id or carms_id in code:
                    program_id = pid
                    break
            
            if not program_id:
                continue
            
            criteria = SelectionCriteria(
                program_id=program_id,
                criterion_type=row['criterion_type'],
                weight_description=row.get('description', ''),
            )
            session.add(criteria)
            inserted_count += 1
        
        session.commit()
    
    logger.info(f"Loaded {inserted_count} selection criteria")
    
    return Output(
        inserted_count,
        metadata={
            "inserted": inserted_count,
        }
    )


@asset(
    ins={
        "staging_training_sites": AssetIn(),
        "fact_programs": AssetIn(),
    },
    group_name="serving",
    description="Load training sites",
)
def dim_training_sites(
    staging_training_sites: pd.DataFrame,
    fact_programs: int,
) -> Output[int]:
    """Populate training sites dimension."""
    logger.info("Loading training sites")
    
    engine = get_engine()
    inserted_count = 0
    
    program_lookup = {}
    
    with Session(engine) as session:
        programs = session.exec(select(Program)).all()
        for prog in programs:
            program_lookup[str(prog.program_code)] = prog.id
        
        for _, row in staging_training_sites.iterrows():
            carms_id = str(row['carms_id'])
            
            # Find matching program
            program_id = None
            for code, pid in program_lookup.items():
                if code in carms_id or carms_id in code:
                    program_id = pid
                    break
            
            if not program_id:
                continue
            
            site = TrainingSite(
                program_id=program_id,
                site_name=row['site_name'],
                site_type=row.get('site_type', 'Hospital'),
            )
            session.add(site)
            inserted_count += 1
        
        session.commit()
    
    logger.info(f"Loaded {inserted_count} training sites")
    
    return Output(
        inserted_count,
        metadata={
            "inserted": inserted_count,
        }
    )


# Export all serving assets
serving_assets = [
    dim_universities,
    dim_specialties,
    fact_programs,
    dim_requirements,
    dim_selection_criteria,
    dim_training_sites,
]
