"""Program API endpoints."""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select, or_, and_, func
from loguru import logger

from src.models.program import Program
from src.models.university import University
from src.models.specialty import Specialty
from src.models.requirement import Requirement
from src.models.selection_criteria import SelectionCriteria
from src.models.training_site import TrainingSite
from src.api.schemas import (
    ProgramListResponse,
    ProgramDetailResponse,
    ProgramFilters,
    ProgramCompareRequest,
    ProgramComparisonResponse,
    RequirementResponse,
    SelectionCriteriaResponse,
    TrainingSiteResponse,
)
from src.api.dependencies import get_session


router = APIRouter()


@router.get("/", response_model=List[ProgramListResponse])
async def list_programs(
    specialty_id: Optional[int] = Query(None, description="Filter by specialty ID"),
    specialty_name: Optional[str] = Query(None, description="Filter by specialty name"),
    university_id: Optional[int] = Query(None, description="Filter by university ID"),
    university_name: Optional[str] = Query(None, description="Filter by university name"),
    province: Optional[str] = Query(None, description="Filter by province"),
    language: Optional[str] = Query(None, description="Filter by language"),
    is_accepting: Optional[bool] = Query(None, description="Filter by application status"),
    min_quota: Optional[int] = Query(None, description="Minimum quota"),
    max_quota: Optional[int] = Query(None, description="Maximum quota"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=500, description="Maximum records to return"),
    session: Session = Depends(get_session),
) -> List[ProgramListResponse]:
    """List programs with optional filters.
    
    Supports filtering by specialty, university, location, language, and quota.
    """
    # Build query
    query = select(Program).where(Program.is_deleted == False)
    
    # Apply filters
    if specialty_id:
        query = query.where(Program.specialty_id == specialty_id)
    
    if specialty_name:
        query = query.join(Specialty).where(
            Specialty.name.ilike(f"%{specialty_name}%")
        )
    
    if university_id:
        query = query.where(Program.university_id == university_id)
    
    if university_name:
        query = query.join(University).where(
            University.name.ilike(f"%{university_name}%")
        )
    
    if province:
        query = query.join(University).where(University.province == province)
    
    if language:
        query = query.where(Program.language.ilike(f"%{language}%"))
    
    if is_accepting is not None:
        query = query.where(Program.is_accepting_applications == is_accepting)
    
    if min_quota is not None:
        query = query.where(Program.quota >= min_quota)
    
    if max_quota is not None:
        query = query.where(Program.quota <= max_quota)
    
    # Apply pagination
    query = query.offset(skip).limit(limit)
    
    # Execute query
    programs = session.exec(query).all()
    
    logger.info(f"Retrieved {len(programs)} programs (skip={skip}, limit={limit})")
    
    return [ProgramListResponse.model_validate(p) for p in programs]


@router.get("/{program_id}", response_model=ProgramDetailResponse)
async def get_program(
    program_id: int,
    session: Session = Depends(get_session),
) -> ProgramDetailResponse:
    """Get detailed information about a specific program.
    
    Includes university, specialty, and full description information.
    """
    # Query program with relationships
    query = (
        select(Program)
        .where(Program.id == program_id)
        .where(Program.is_deleted == False)
    )
    
    program = session.exec(query).first()
    
    if not program:
        raise HTTPException(status_code=404, detail="Program not found")
    
    # Manually load relationships for response
    response_data = ProgramDetailResponse.model_validate(program)
    
    # Load university
    university = session.get(University, program.university_id)
    if university:
        response_data.university = university
    
    # Load specialty
    specialty = session.get(Specialty, program.specialty_id)
    if specialty:
        response_data.specialty = specialty
    
    logger.info(f"Retrieved program {program_id}: {program.program_name}")
    
    return response_data


@router.get("/{program_id}/requirements", response_model=List[RequirementResponse])
async def get_program_requirements(
    program_id: int,
    session: Session = Depends(get_session),
) -> List[RequirementResponse]:
    """Get all requirements for a specific program.
    
    Returns eligibility, prerequisites, language requirements, etc.
    """
    # Verify program exists
    program = session.get(Program, program_id)
    if not program or program.is_deleted:
        raise HTTPException(status_code=404, detail="Program not found")
    
    # Get requirements
    query = select(Requirement).where(Requirement.program_id == program_id)
    requirements = session.exec(query).all()
    
    logger.info(f"Retrieved {len(requirements)} requirements for program {program_id}")
    
    return [RequirementResponse.model_validate(r) for r in requirements]


@router.get("/{program_id}/selection-criteria", response_model=List[SelectionCriteriaResponse])
async def get_program_selection_criteria(
    program_id: int,
    session: Session = Depends(get_session),
) -> List[SelectionCriteriaResponse]:
    """Get selection criteria for a specific program.
    
    Shows what the program values in applicants.
    """
    # Verify program exists
    program = session.get(Program, program_id)
    if not program or program.is_deleted:
        raise HTTPException(status_code=404, detail="Program not found")
    
    # Get selection criteria
    query = select(SelectionCriteria).where(SelectionCriteria.program_id == program_id)
    criteria = session.exec(query).all()
    
    logger.info(f"Retrieved {len(criteria)} selection criteria for program {program_id}")
    
    return [SelectionCriteriaResponse.model_validate(c) for c in criteria]


@router.get("/{program_id}/training-sites", response_model=List[TrainingSiteResponse])
async def get_program_training_sites(
    program_id: int,
    session: Session = Depends(get_session),
) -> List[TrainingSiteResponse]:
    """Get training sites for a specific program.
    
    Lists hospitals and clinical sites where training occurs.
    """
    # Verify program exists
    program = session.get(Program, program_id)
    if not program or program.is_deleted:
        raise HTTPException(status_code=404, detail="Program not found")
    
    # Get training sites
    query = select(TrainingSite).where(TrainingSite.program_id == program_id)
    sites = session.exec(query).all()
    
    logger.info(f"Retrieved {len(sites)} training sites for program {program_id}")
    
    return [TrainingSiteResponse.model_validate(s) for s in sites]


@router.post("/compare", response_model=ProgramComparisonResponse)
async def compare_programs(
    request: ProgramCompareRequest,
    session: Session = Depends(get_session),
) -> ProgramComparisonResponse:
    """Compare multiple programs side-by-side.
    
    Retrieves full details for multiple programs for comparison.
    """
    # Get all programs
    query = (
        select(Program)
        .where(Program.id.in_(request.program_ids))
        .where(Program.is_deleted == False)
    )
    programs = session.exec(query).all()
    
    if len(programs) < len(request.program_ids):
        found_ids = [p.id for p in programs]
        missing_ids = [pid for pid in request.program_ids if pid not in found_ids]
        logger.warning(f"Some programs not found: {missing_ids}")
    
    # Build detailed responses
    detailed_programs = []
    for program in programs:
        detail = ProgramDetailResponse.model_validate(program)
        
        # Load relationships
        university = session.get(University, program.university_id)
        if university:
            detail.university = university
        
        specialty = session.get(Specialty, program.specialty_id)
        if specialty:
            detail.specialty = specialty
        
        detailed_programs.append(detail)
    
    # Build comparison matrix
    comparison_matrix = {
        "basic_info": {
            "program_codes": [p.program_code for p in detailed_programs],
            "program_names": [p.program_name for p in detailed_programs],
            "universities": [p.university.name if p.university else None for p in detailed_programs],
            "specialties": [p.specialty.name if p.specialty else None for p in detailed_programs],
        },
        "capacity": {
            "quotas": [p.quota for p in detailed_programs],
            "backup_quotas": [p.backup_quota for p in detailed_programs],
        },
        "details": {
            "languages": [p.language for p in detailed_programs],
            "training_duration": [p.training_duration_years for p in detailed_programs],
            "application_deadlines": [str(p.application_deadline) if p.application_deadline else None for p in detailed_programs],
        }
    }
    
    logger.info(f"Compared {len(detailed_programs)} programs")
    
    return ProgramComparisonResponse(
        programs=detailed_programs,
        comparison_matrix=comparison_matrix,
    )
