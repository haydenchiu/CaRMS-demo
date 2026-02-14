"""Analytics API endpoints."""

from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlmodel import Session, select, func
from loguru import logger

from src.models.program import Program
from src.models.university import University
from src.models.specialty import Specialty
from src.models.requirement import Requirement
from src.models.selection_criteria import SelectionCriteria
from src.api.schemas import (
    SpecialtyStatsResponse,
    RequirementSummaryResponse,
    SelectionCriteriaTrendResponse,
    GeographicDistributionResponse,
)
from src.api.dependencies import get_session


router = APIRouter()


@router.get("/specialties", response_model=List[SpecialtyStatsResponse])
async def get_specialty_statistics(
    category: Optional[str] = Query(None, description="Filter by specialty category"),
    min_programs: Optional[int] = Query(None, description="Minimum number of programs"),
    session: Session = Depends(get_session),
) -> List[SpecialtyStatsResponse]:
    """Get statistics for each specialty.
    
    Shows program counts, total quotas, and average quotas per specialty.
    """
    # Build query
    query = (
        select(
            Specialty.id.label('specialty_id'),
            Specialty.name.label('specialty_name'),
            Specialty.category.label('specialty_category'),
            func.count(Program.id).label('program_count'),
            func.sum(func.coalesce(Program.quota, 0)).label('total_quota'),
            func.count(func.distinct(University.id)).label('universities_offering'),
        )
        .join(Program, Program.specialty_id == Specialty.id)
        .join(University, Program.university_id == University.id)
        .where(Program.is_deleted == False)
        .group_by(Specialty.id, Specialty.name, Specialty.category)
    )
    
    # Apply filters
    if category:
        query = query.where(Specialty.category == category)
    
    if min_programs:
        query = query.having(func.count(Program.id) >= min_programs)
    
    # Order by program count descending
    query = query.order_by(func.count(Program.id).desc())
    
    results = session.exec(query).all()
    
    # Build response
    stats = []
    for r in results:
        avg_quota = float(r.total_quota) / r.program_count if r.program_count > 0 else 0.0
        stats.append(SpecialtyStatsResponse(
            specialty_id=r.specialty_id,
            specialty_name=r.specialty_name,
            specialty_category=r.specialty_category or 'Other',
            program_count=r.program_count,
            total_quota=r.total_quota or 0,
            avg_quota_per_program=round(avg_quota, 2),
            universities_offering=r.universities_offering,
        ))
    
    logger.info(f"Retrieved statistics for {len(stats)} specialties")
    
    return stats


@router.get("/requirements/summary", response_model=List[RequirementSummaryResponse])
async def get_requirements_summary(
    specialty_id: Optional[int] = Query(None, description="Filter by specialty ID"),
    requirement_type: Optional[str] = Query(None, description="Filter by requirement type"),
    session: Session = Depends(get_session),
) -> List[RequirementSummaryResponse]:
    """Get summary of requirements by specialty.
    
    Shows distribution of requirement types across specialties.
    """
    query = (
        select(
            Specialty.name.label('specialty_name'),
            Requirement.requirement_type,
            func.count(Requirement.id).label('requirement_count'),
            func.sum(func.cast(Requirement.is_mandatory, func.Integer())).label('mandatory_count'),
        )
        .join(Program, Requirement.program_id == Program.id)
        .join(Specialty, Program.specialty_id == Specialty.id)
        .where(Program.is_deleted == False)
        .group_by(Specialty.name, Requirement.requirement_type)
    )
    
    # Apply filters
    if specialty_id:
        query = query.where(Specialty.id == specialty_id)
    
    if requirement_type:
        query = query.where(Requirement.requirement_type == requirement_type)
    
    # Order by count
    query = query.order_by(func.count(Requirement.id).desc())
    
    results = session.exec(query).all()
    
    # Build response
    summaries = []
    for r in results:
        mandatory_count = r.mandatory_count or 0
        summaries.append(RequirementSummaryResponse(
            specialty_name=r.specialty_name,
            requirement_type=r.requirement_type,
            requirement_count=r.requirement_count,
            mandatory_count=mandatory_count,
            optional_count=r.requirement_count - mandatory_count,
        ))
    
    logger.info(f"Retrieved requirement summaries for {len(summaries)} specialty-type combinations")
    
    return summaries


@router.get("/selection-criteria", response_model=List[SelectionCriteriaTrendResponse])
async def get_selection_criteria_trends(
    specialty_category: Optional[str] = Query(None, description="Filter by specialty category"),
    session: Session = Depends(get_session),
) -> List[SelectionCriteriaTrendResponse]:
    """Get trends in selection criteria across specialties.
    
    Shows what criteria are most commonly mentioned.
    """
    query = (
        select(
            Specialty.category.label('specialty_category'),
            SelectionCriteria.criterion_type,
            func.count(SelectionCriteria.id).label('mention_count'),
            func.count(func.distinct(Program.id)).label('program_count'),
        )
        .join(Program, SelectionCriteria.program_id == Program.id)
        .join(Specialty, Program.specialty_id == Specialty.id)
        .where(Program.is_deleted == False)
        .group_by(Specialty.category, SelectionCriteria.criterion_type)
    )
    
    # Apply filters
    if specialty_category:
        query = query.where(Specialty.category == specialty_category)
    
    # Order by mention count
    query = query.order_by(func.count(SelectionCriteria.id).desc())
    
    results = session.exec(query).all()
    
    # Build response
    trends = []
    for r in results:
        avg_mentions = float(r.mention_count) / r.program_count if r.program_count > 0 else 0.0
        trends.append(SelectionCriteriaTrendResponse(
            specialty_category=r.specialty_category or 'Other',
            criterion_type=r.criterion_type,
            mention_count=r.mention_count,
            program_count=r.program_count,
            avg_mentions_per_program=round(avg_mentions, 2),
        ))
    
    logger.info(f"Retrieved selection criteria trends for {len(trends)} category-criterion combinations")
    
    return trends


@router.get("/geographic-distribution", response_model=List[GeographicDistributionResponse])
async def get_geographic_distribution(
    province: Optional[str] = Query(None, description="Filter by province"),
    specialty_category: Optional[str] = Query(None, description="Filter by specialty category"),
    session: Session = Depends(get_session),
) -> List[GeographicDistributionResponse]:
    """Get geographic distribution of programs.
    
    Shows programs by province, city, and specialty category.
    """
    query = (
        select(
            University.province,
            University.city,
            Specialty.category.label('specialty_category'),
            func.count(Program.id).label('program_count'),
            func.sum(func.coalesce(Program.quota, 0)).label('total_quota'),
        )
        .join(University, Program.university_id == University.id)
        .join(Specialty, Program.specialty_id == Specialty.id)
        .where(Program.is_deleted == False)
        .group_by(University.province, University.city, Specialty.category)
    )
    
    # Apply filters
    if province:
        query = query.where(University.province == province)
    
    if specialty_category:
        query = query.where(Specialty.category == specialty_category)
    
    # Order by program count
    query = query.order_by(func.count(Program.id).desc())
    
    results = session.exec(query).all()
    
    # Build response
    distributions = []
    for r in results:
        distributions.append(GeographicDistributionResponse(
            province=r.province or 'Unknown',
            city=r.city,
            specialty_category=r.specialty_category or 'Other',
            program_count=r.program_count,
            total_quota=r.total_quota or 0,
        ))
    
    logger.info(f"Retrieved geographic distribution for {len(distributions)} location-specialty combinations")
    
    return distributions


@router.get("/provinces", response_model=List[dict])
async def get_provinces(
    session: Session = Depends(get_session),
) -> List[dict]:
    """Get list of provinces with program counts.
    
    Useful for building filters and UI.
    """
    query = (
        select(
            University.province,
            func.count(func.distinct(Program.id)).label('program_count'),
            func.count(func.distinct(University.id)).label('university_count'),
        )
        .join(Program, Program.university_id == University.id)
        .where(Program.is_deleted == False)
        .where(University.province.is_not(None))
        .group_by(University.province)
        .order_by(func.count(func.distinct(Program.id)).desc())
    )
    
    results = session.exec(query).all()
    
    provinces = [
        {
            "province": r.province,
            "program_count": r.program_count,
            "university_count": r.university_count,
        }
        for r in results
    ]
    
    logger.info(f"Retrieved data for {len(provinces)} provinces")
    
    return provinces
