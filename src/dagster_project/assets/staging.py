"""Staging layer assets.

These assets transform raw data into cleaned, validated staging tables.
"""

import re
import pandas as pd
from typing import Dict, Any, List, Optional
from dagster import asset, AssetIn, Output, MetadataValue
from loguru import logger


@asset(
    ins={"raw_program_master": AssetIn()},
    group_name="staging",
    description="Parse and clean program master data",
)
def staging_programs(raw_program_master: pd.DataFrame) -> pd.DataFrame:
    """Transform raw program master data into clean staging format.
    
    Extracts core program information, handles missing values,
    and standardizes data types.
    """
    logger.info("Processing program master data")
    
    df = raw_program_master.copy()
    
    # Rename columns to match our schema
    df = df.rename(columns={
        'discipline_id': 'discipline_id',
        'discipline_name': 'specialty_name',
        'school_id': 'university_id',
        'school_name': 'university_name',
        'program_stream_id': 'program_code',
        'program_stream_name': 'program_stream',
        'program_site': 'program_site',
        'program_name': 'program_name'
    })
    
    # Extract relevant columns
    staging_df = pd.DataFrame({
        'program_code': df['program_code'].astype(str),
        'program_name': df['program_name'].fillna(''),
        'program_stream': df['program_stream'].fillna(''),
        'program_site': df['program_site'].fillna(''),
        'specialty_name': df['specialty_name'].fillna(''),
        'specialty_id_raw': df['discipline_id'],
        'university_name': df['university_name'].fillna(''),
        'university_id_raw': df['university_id'],
    })
    
    # Clean up program codes
    staging_df['program_code'] = staging_df['program_code'].str.strip()
    
    # Extract program metadata
    staging_df['carms_year'] = 2025  # Based on filename 1503
    staging_df['source_file'] = '1503_program_master.xlsx'
    
    # Data quality flags
    staging_df['is_valid'] = True
    staging_df.loc[staging_df['program_code'].str.len() < 3, 'is_valid'] = False
    staging_df.loc[staging_df['university_name'] == '', 'is_valid'] = False
    
    logger.info(f"Processed {len(staging_df)} programs, {staging_df['is_valid'].sum()} valid")
    
    return staging_df


@asset(
    ins={"staging_programs": AssetIn()},
    group_name="staging",
    description="Extract and standardize university information",
)
def staging_universities(staging_programs: pd.DataFrame) -> pd.DataFrame:
    """Extract unique universities from staging programs.
    
    Creates a clean university dimension table.
    """
    logger.info("Extracting university data")
    
    # Get unique universities
    universities = staging_programs[['university_name', 'university_id_raw']].drop_duplicates()
    
    # Parse province/city from university name where possible
    # Common patterns: "University of Toronto", "McGill University", etc.
    province_map = {
        'Toronto': 'Ontario',
        'McGill': 'Quebec',
        'Montreal': 'Quebec',
        'UBC': 'British Columbia',
        'Vancouver': 'British Columbia',
        'Alberta': 'Alberta',
        'Calgary': 'Alberta',
        'Edmonton': 'Alberta',
        'Manitoba': 'Manitoba',
        'Winnipeg': 'Manitoba',
        'Saskatchewan': 'Saskatchewan',
        'Saskatoon': 'Saskatchewan',
        'Regina': 'Saskatchewan',
        'Dalhousie': 'Nova Scotia',
        'Halifax': 'Nova Scotia',
        'Memorial': 'Newfoundland and Labrador',
        'Newfoundland': 'Newfoundland and Labrador',
        'Ottawa': 'Ontario',
        'Queen': 'Ontario',
        'Kingston': 'Ontario',
        'McMaster': 'Ontario',
        'Hamilton': 'Ontario',
        'Western': 'Ontario',
        'London': 'Ontario',
        'Laval': 'Quebec',
        'Sherbrooke': 'Quebec',
    }
    
    def extract_province(name: str) -> str:
        """Extract province from university name."""
        for keyword, province in province_map.items():
            if keyword.lower() in name.lower():
                return province
        return None
    
    universities = universities.copy()
    universities['province'] = universities['university_name'].apply(extract_province)
    
    # Generate university codes (first letter + first 3 consonants)
    def generate_code(name: str) -> str:
        """Generate a simple code from university name."""
        words = name.split()
        if len(words) > 0:
            # Use initials for multi-word names
            if len(words) >= 2:
                return ''.join([w[0] for w in words if len(w) > 0])[:4].upper()
            # Use first 4 letters for single word
            return name[:4].upper()
        return 'UNK'
    
    universities['code'] = universities['university_name'].apply(generate_code)
    
    # Detect francophone universities
    francophone_keywords = ['laval', 'montreal', 'sherbrooke', 'mcgill']
    universities['is_francophone'] = universities['university_name'].str.lower().apply(
        lambda x: any(keyword in x for keyword in francophone_keywords)
    )
    
    logger.info(f"Extracted {len(universities)} unique universities")
    
    return universities.reset_index(drop=True)


@asset(
    ins={"raw_discipline": AssetIn()},
    group_name="staging",
    description="Extract and categorize medical specialties",
)
def staging_specialties(raw_discipline: pd.DataFrame) -> pd.DataFrame:
    """Transform discipline data into specialty dimension.
    
    Categorizes specialties and handles parent-child relationships.
    """
    logger.info("Processing specialty data")
    
    df = raw_discipline.copy()
    
    # Rename columns
    df = df.rename(columns={
        'discipline_id': 'specialty_id_raw',
        'discipline': 'specialty_name'
    })
    
    # Generate specialty codes (first letter + first 2 letters of main word)
    def generate_specialty_code(name: str) -> str:
        """Generate a code from specialty name."""
        # Remove suffixes like "- Clinician Investigator Program"
        clean_name = re.split(r'\s*-\s*', name)[0]
        words = clean_name.split()
        if len(words) > 1:
            return ''.join([w[0] for w in words])[:3].upper()
        return clean_name[:3].upper()
    
    df['code'] = df['specialty_name'].apply(generate_specialty_code)
    
    # Categorize specialties
    surgical_keywords = ['surgery', 'surgical']
    medical_keywords = ['medicine', 'medical']
    primary_care_keywords = ['family medicine', 'family', 'general practice']
    
    def categorize_specialty(name: str) -> str:
        """Categorize specialty into broad category."""
        name_lower = name.lower()
        
        if any(kw in name_lower for kw in primary_care_keywords):
            return 'Primary Care'
        elif any(kw in name_lower for kw in surgical_keywords):
            return 'Surgical'
        elif any(kw in name_lower for kw in medical_keywords):
            return 'Medical'
        elif 'psychiatry' in name_lower:
            return 'Psychiatry'
        elif 'pediatric' in name_lower or 'paediatric' in name_lower:
            return 'Pediatrics'
        elif 'obstetric' in name_lower or 'gynecol' in name_lower:
            return 'Obstetrics & Gynecology'
        elif 'diagnostic' in name_lower or 'radiology' in name_lower:
            return 'Diagnostic'
        elif 'pathology' in name_lower:
            return 'Laboratory'
        else:
            return 'Other'
    
    df['category'] = df['specialty_name'].apply(categorize_specialty)
    
    # Detect if it's a sub-specialty (has " - " in name)
    df['is_subspecialty'] = df['specialty_name'].str.contains(' - ', regex=False)
    
    # Extract parent specialty for subspecialties
    df['parent_specialty_name'] = df['specialty_name'].apply(
        lambda x: re.split(r'\s*-\s*', x)[0] if ' - ' in x else None
    )
    
    # Flag primary care specialties
    df['is_primary_care'] = df['category'] == 'Primary Care'
    
    logger.info(f"Processed {len(df)} specialties across {df['category'].nunique()} categories")
    
    return df


@asset(
    ins={
        "raw_program_descriptions_json": AssetIn(),
        "staging_programs": AssetIn(),
    },
    group_name="staging",
    description="Parse and extract program descriptions and metadata",
)
def staging_program_descriptions(
    raw_program_descriptions_json: list,
    staging_programs: pd.DataFrame
) -> pd.DataFrame:
    """Parse program descriptions from JSON and extract structured information.
    
    Extracts rich text content and metadata from program descriptions.
    """
    logger.info("Processing program descriptions from JSON")
    
    descriptions = []
    
    for item in raw_program_descriptions_json:
        program_id = item.get('id', '')
        page_content = item.get('page_content', '')
        metadata = item.get('metadata', {})
        
        # Extract program code from ID (format: "1503|27447" -> program code from URL)
        carms_id = program_id.split('|')[-1] if '|' in program_id else program_id
        
        # Parse markdown sections
        sections = {}
        current_section = None
        current_content = []
        
        for line in page_content.split('\n'):
            # Headers start with #
            if line.startswith('#'):
                # Save previous section
                if current_section:
                    sections[current_section] = '\n'.join(current_content).strip()
                
                # Start new section
                current_section = line.lstrip('#').strip()
                current_content = []
            else:
                current_content.append(line)
        
        # Save last section
        if current_section:
            sections[current_section] = '\n'.join(current_content).strip()
        
        descriptions.append({
            'carms_id': carms_id,
            'source_url': metadata.get('source', ''),
            'full_content': page_content,
            'program_overview': sections.get('Program Overview', ''),
            'curriculum': sections.get('Curriculum', sections.get('Curriculum Highlights', '')),
            'selection_criteria': sections.get('Selection Criteria', ''),
            'application_process': sections.get('Application Process', ''),
            'contact_info': sections.get('Contact Information', ''),
            'content_sections': list(sections.keys()),
            'total_length': len(page_content),
        })
    
    df = pd.DataFrame(descriptions)
    
    logger.info(f"Processed {len(df)} program descriptions")
    logger.info(f"Average content length: {df['total_length'].mean():.0f} characters")
    
    return df


@asset(
    ins={"staging_program_descriptions": AssetIn()},
    group_name="staging",
    description="Extract program requirements from descriptions",
)
def staging_requirements(staging_program_descriptions: pd.DataFrame) -> pd.DataFrame:
    """Extract structured requirements from program descriptions.
    
    Parses requirements like eligibility, prerequisites, language requirements.
    """
    logger.info("Extracting program requirements")
    
    requirements = []
    
    for idx, row in staging_program_descriptions.iterrows():
        carms_id = row['carms_id']
        content = row['full_content']
        
        # Extract different requirement types using regex patterns
        requirement_patterns = {
            'Eligibility': r'(?i)eligibility[:\s]+(.*?)(?=\n\n|\n#|$)',
            'Prerequisites': r'(?i)prerequisite[s]?[:\s]+(.*?)(?=\n\n|\n#|$)',
            'Language': r'(?i)language requirement[s]?[:\s]+(.*?)(?=\n\n|\n#|$)',
            'Citizenship': r'(?i)citizenship[:\s]+(.*?)(?=\n\n|\n#|$)',
            'Visa': r'(?i)visa[:\s]+(.*?)(?=\n\n|\n#|$)',
        }
        
        for req_type, pattern in requirement_patterns.items():
            matches = re.findall(pattern, content, re.DOTALL)
            for match in matches:
                requirement_text = match.strip()[:500]  # Limit length
                if requirement_text:
                    requirements.append({
                        'carms_id': carms_id,
                        'requirement_type': req_type,
                        'requirement_text': requirement_text,
                        'is_mandatory': 'required' in requirement_text.lower() or 'must' in requirement_text.lower(),
                    })
    
    df = pd.DataFrame(requirements) if requirements else pd.DataFrame(columns=[
        'carms_id', 'requirement_type', 'requirement_text', 'is_mandatory'
    ])
    
    logger.info(f"Extracted {len(df)} requirements")
    if len(df) > 0:
        logger.info(f"Requirement types: {df['requirement_type'].value_counts().to_dict()}")
    
    return df


@asset(
    ins={"staging_program_descriptions": AssetIn()},
    group_name="staging",
    description="Extract selection criteria from program descriptions",
)
def staging_selection_criteria(staging_program_descriptions: pd.DataFrame) -> pd.DataFrame:
    """Extract and structure selection criteria from descriptions.
    
    Identifies what programs look for in applicants.
    """
    logger.info("Extracting selection criteria")
    
    criteria_list = []
    
    # Common criteria keywords
    criteria_keywords = {
        'Academic Performance': ['academic', 'grades', 'gpa', 'transcript', 'scores'],
        'Research': ['research', 'publications', 'scholarly'],
        'Clinical Skills': ['clinical', 'clerkship', 'rotations', 'electives'],
        'Leadership': ['leadership', 'extracurricular', 'volunteer'],
        'Personal Qualities': ['personal', 'character', 'integrity', 'compassion'],
        'Interview Performance': ['interview', 'mmi', 'communication'],
        'References': ['reference', 'letter', 'recommendation'],
        'Fit': ['fit', 'alignment', 'values', 'culture'],
    }
    
    for idx, row in staging_program_descriptions.iterrows():
        carms_id = row['carms_id']
        content = row.get('selection_criteria', '') + ' ' + row.get('full_content', '')
        content_lower = content.lower()
        
        # Check for each criterion type
        for criterion_type, keywords in criteria_keywords.items():
            # Count keyword mentions
            mentions = sum(1 for keyword in keywords if keyword in content_lower)
            
            if mentions > 0:
                # Extract relevant excerpt (up to 200 chars around first keyword)
                first_keyword = next(kw for kw in keywords if kw in content_lower)
                pos = content_lower.find(first_keyword)
                start = max(0, pos - 100)
                end = min(len(content), pos + 100)
                excerpt = content[start:end].strip()
                
                criteria_list.append({
                    'carms_id': carms_id,
                    'criterion_type': criterion_type,
                    'mentions': mentions,
                    'description': excerpt[:200],
                })
    
    df = pd.DataFrame(criteria_list) if criteria_list else pd.DataFrame(columns=[
        'carms_id', 'criterion_type', 'mentions', 'description'
    ])
    
    logger.info(f"Extracted {len(df)} selection criteria")
    if len(df) > 0:
        logger.info(f"Top criteria: {df.groupby('criterion_type')['mentions'].sum().sort_values(ascending=False).head()}")
    
    return df


@asset(
    ins={"staging_program_descriptions": AssetIn()},
    group_name="staging",
    description="Extract training site information from descriptions",
)
def staging_training_sites(staging_program_descriptions: pd.DataFrame) -> pd.DataFrame:
    """Extract training site/location information from descriptions.
    
    Identifies clinical training locations mentioned in program descriptions.
    """
    logger.info("Extracting training site information")
    
    sites = []
    
    # Common site keywords
    site_keywords = [
        'hospital', 'medical center', 'health centre', 'clinic', 
        'training site', 'rotation site', 'teaching hospital'
    ]
    
    for idx, row in staging_program_descriptions.iterrows():
        carms_id = row['carms_id']
        content = row['full_content']
        
        # Look for sections about training sites
        if 'training' in content.lower() or 'rotation' in content.lower() or 'site' in content.lower():
            # Extract sentences mentioning hospitals/sites
            sentences = content.split('.')
            
            for sentence in sentences:
                sentence_lower = sentence.lower()
                if any(keyword in sentence_lower for keyword in site_keywords):
                    # Extract potential site name (capitalize words that might be names)
                    site_name = sentence.strip()[:200]
                    
                    # Determine site type
                    site_type = 'Hospital'
                    if 'clinic' in sentence_lower:
                        site_type = 'Clinic'
                    elif 'community' in sentence_lower:
                        site_type = 'Community'
                    elif 'academic' in sentence_lower or 'teaching' in sentence_lower:
                        site_type = 'Academic Medical Center'
                    
                    sites.append({
                        'carms_id': carms_id,
                        'site_name': site_name,
                        'site_type': site_type,
                    })
    
    df = pd.DataFrame(sites) if sites else pd.DataFrame(columns=[
        'carms_id', 'site_name', 'site_type'
    ])
    
    # Remove duplicates
    if len(df) > 0:
        df = df.drop_duplicates(subset=['carms_id', 'site_name'])
    
    logger.info(f"Extracted {len(df)} training site references")
    
    return df


# Export all staging assets
staging_assets = [
    staging_programs,
    staging_universities,
    staging_specialties,
    staging_program_descriptions,
    staging_requirements,
    staging_selection_criteria,
    staging_training_sites,
]
