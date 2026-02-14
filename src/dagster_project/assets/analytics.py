"""Analytics layer assets.

These assets create aggregated analytics tables for reporting and analysis.
"""

import pandas as pd
from typing import Dict, Any
from sqlmodel import Session, select, func
from dagster import asset, AssetIn, Output, MetadataValue
from loguru import logger

from src.models.university import University
from src.models.specialty import Specialty
from src.models.program import Program
from src.models.requirement import Requirement
from src.models.selection_criteria import SelectionCriteria
from src.models.training_site import TrainingSite
from src.utils.database import get_engine


@asset(
    ins={"fact_programs": AssetIn()},
    group_name="analytics",
    description="Aggregate program statistics by specialty",
)
def analytics_program_summary(fact_programs: int) -> pd.DataFrame:
    """Create summary statistics of programs by specialty and university.
    
    Provides overview metrics for reporting and dashboards.
    """
    logger.info("Building program summary analytics")
    
    engine = get_engine()
    
    with Session(engine) as session:
        # Query programs with their dimensions
        query = (
            select(
                Specialty.name.label('specialty_name'),
                Specialty.category.label('specialty_category'),
                University.name.label('university_name'),
                University.province.label('province'),
                func.count(Program.id).label('program_count'),
                func.sum(func.coalesce(Program.quota, 0)).label('total_quota'),
            )
            .join(Specialty, Program.specialty_id == Specialty.id)
            .join(University, Program.university_id == University.id)
            .where(Program.is_deleted == False)
            .group_by(
                Specialty.name,
                Specialty.category,
                University.name,
                University.province,
            )
        )
        
        results = session.exec(query).all()
        
        # Convert to DataFrame
        df = pd.DataFrame([
            {
                'specialty_name': r.specialty_name,
                'specialty_category': r.specialty_category,
                'university_name': r.university_name,
                'province': r.province,
                'program_count': r.program_count,
                'total_quota': r.total_quota or 0,
            }
            for r in results
        ])
    
    if len(df) > 0:
        logger.info(f"Generated summary for {len(df)} specialty-university combinations")
        logger.info(f"Total programs: {df['program_count'].sum()}")
        logger.info(f"Total quota: {df['total_quota'].sum()}")
    else:
        logger.warning("No program data found for analytics")
    
    return df


@asset(
    ins={"dim_requirements": AssetIn()},
    group_name="analytics",
    description="Analyze requirements by specialty",
)
def analytics_requirements_by_specialty(dim_requirements: int) -> pd.DataFrame:
    """Aggregate requirement types by specialty.
    
    Helps understand common requirements across different specialties.
    """
    logger.info("Analyzing requirements by specialty")
    
    engine = get_engine()
    
    with Session(engine) as session:
        query = (
            select(
                Specialty.name.label('specialty_name'),
                Specialty.category.label('specialty_category'),
                Requirement.requirement_type,
                func.count(Requirement.id).label('requirement_count'),
                func.sum(func.cast(Requirement.is_mandatory, func.Integer())).label('mandatory_count'),
            )
            .join(Program, Requirement.program_id == Program.id)
            .join(Specialty, Program.specialty_id == Specialty.id)
            .group_by(
                Specialty.name,
                Specialty.category,
                Requirement.requirement_type,
            )
        )
        
        results = session.exec(query).all()
        
        df = pd.DataFrame([
            {
                'specialty_name': r.specialty_name,
                'specialty_category': r.specialty_category,
                'requirement_type': r.requirement_type,
                'requirement_count': r.requirement_count,
                'mandatory_count': r.mandatory_count or 0,
                'optional_count': r.requirement_count - (r.mandatory_count or 0),
            }
            for r in results
        ])
    
    if len(df) > 0:
        logger.info(f"Analyzed {len(df)} requirement-specialty combinations")
        logger.info(f"Top requirements: {df.groupby('requirement_type')['requirement_count'].sum().sort_values(ascending=False).head()}")
    
    return df


@asset(
    ins={"dim_selection_criteria": AssetIn()},
    group_name="analytics",
    description="Analyze selection criteria patterns across specialties",
)
def analytics_selection_criteria_trends(dim_selection_criteria: int) -> pd.DataFrame:
    """Identify common selection criteria patterns.
    
    Shows what criteria are most valued across different specialties.
    """
    logger.info("Analyzing selection criteria trends")
    
    engine = get_engine()
    
    with Session(engine) as session:
        query = (
            select(
                Specialty.category.label('specialty_category'),
                SelectionCriteria.criterion_type,
                func.count(SelectionCriteria.id).label('mention_count'),
                func.count(func.distinct(Program.id)).label('program_count'),
            )
            .join(Program, SelectionCriteria.program_id == Program.id)
            .join(Specialty, Program.specialty_id == Specialty.id)
            .group_by(
                Specialty.category,
                SelectionCriteria.criterion_type,
            )
        )
        
        results = session.exec(query).all()
        
        df = pd.DataFrame([
            {
                'specialty_category': r.specialty_category,
                'criterion_type': r.criterion_type,
                'mention_count': r.mention_count,
                'program_count': r.program_count,
                'avg_mentions_per_program': r.mention_count / r.program_count if r.program_count > 0 else 0,
            }
            for r in results
        ])
    
    if len(df) > 0:
        logger.info(f"Analyzed {len(df)} criteria-category combinations")
        logger.info(f"Top criteria by mentions: {df.nlargest(5, 'mention_count')[['criterion_type', 'mention_count']]}")
    
    return df


@asset(
    ins={"fact_programs": AssetIn()},
    group_name="analytics",
    description="Analyze geographic distribution of programs",
)
def analytics_geographic_distribution(fact_programs: int) -> pd.DataFrame:
    """Analyze program distribution across provinces and cities.
    
    Provides geographic insights for applicants and planning.
    """
    logger.info("Analyzing geographic distribution")
    
    engine = get_engine()
    
    with Session(engine) as session:
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
            .group_by(
                University.province,
                University.city,
                Specialty.category,
            )
        )
        
        results = session.exec(query).all()
        
        df = pd.DataFrame([
            {
                'province': r.province or 'Unknown',
                'city': r.city or 'Unknown',
                'specialty_category': r.specialty_category,
                'program_count': r.program_count,
                'total_quota': r.total_quota or 0,
            }
            for r in results
        ])
    
    if len(df) > 0:
        logger.info(f"Geographic distribution across {df['province'].nunique()} provinces")
        logger.info(f"Programs by province:\n{df.groupby('province')['program_count'].sum().sort_values(ascending=False)}")
    
    return df


@asset(
    ins={"analytics_program_summary": AssetIn()},
    group_name="analytics",
    description="Calculate specialty competitiveness metrics",
)
def analytics_specialty_competitiveness(analytics_program_summary: pd.DataFrame) -> pd.DataFrame:
    """Calculate competitiveness indicators for each specialty.
    
    Helps applicants understand relative competitiveness.
    """
    logger.info("Calculating specialty competitiveness metrics")
    
    if len(analytics_program_summary) == 0:
        logger.warning("No program summary data available")
        return pd.DataFrame(columns=['specialty_name', 'program_count', 'total_quota', 'avg_quota_per_program'])
    
    # Aggregate by specialty
    specialty_stats = analytics_program_summary.groupby('specialty_name').agg({
        'program_count': 'sum',
        'total_quota': 'sum',
    }).reset_index()
    
    # Calculate metrics
    specialty_stats['avg_quota_per_program'] = (
        specialty_stats['total_quota'] / specialty_stats['program_count']
    ).round(2)
    
    # Add competitiveness ranking (lower quota = more competitive)
    specialty_stats['competitiveness_rank'] = specialty_stats['avg_quota_per_program'].rank(ascending=True)
    
    # Categorize competitiveness
    def categorize_competitiveness(rank, total):
        pct = rank / total
        if pct <= 0.33:
            return 'Highly Competitive'
        elif pct <= 0.66:
            return 'Moderately Competitive'
        else:
            return 'Less Competitive'
    
    total_specialties = len(specialty_stats)
    specialty_stats['competitiveness_category'] = specialty_stats['competitiveness_rank'].apply(
        lambda r: categorize_competitiveness(r, total_specialties)
    )
    
    logger.info(f"Calculated competitiveness for {len(specialty_stats)} specialties")
    logger.info(f"Most competitive: {specialty_stats.nsmallest(3, 'avg_quota_per_program')['specialty_name'].tolist()}")
    
    return specialty_stats


# Export all analytics assets
analytics_assets = [
    analytics_program_summary,
    analytics_requirements_by_specialty,
    analytics_selection_criteria_trends,
    analytics_geographic_distribution,
    analytics_specialty_competitiveness,
]
