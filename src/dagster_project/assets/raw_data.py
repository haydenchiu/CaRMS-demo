"""Raw data ingestion assets.

These assets load data from source files without transformation.
"""

import json
import pandas as pd
from pathlib import Path
from typing import Dict, Any
from dagster import asset, Output, MetadataValue
from loguru import logger


DATA_DIR = Path("data")


@asset(
    group_name="raw_data",
    description="Load raw program descriptions from JSON file",
)
def raw_program_descriptions_json() -> list:
    """Load program descriptions from JSON file.
    
    Returns:
        List containing program descriptions with markdown content.
    """
    file_path = DATA_DIR / "1503_markdown_program_descriptions_v2.json"
    
    logger.info(f"Loading program descriptions from {file_path}")
    
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    num_programs = len(data) if isinstance(data, list) else len(data.keys())
    
    logger.info(f"Loaded {num_programs} program descriptions")
    
    # Return just the data - Dagster will handle it
    return data


@asset(
    group_name="raw_data",
    description="Load raw program descriptions from CSV file (cross-sectional)",
)
def raw_program_descriptions_csv() -> pd.DataFrame:
    """Load program descriptions cross-sectional data from CSV.
    
    Returns:
        DataFrame with structured program sections.
    """
    file_path = DATA_DIR / "1503_program_descriptions_x_section.csv"
    
    logger.info(f"Loading program descriptions from {file_path}")
    
    df = pd.read_csv(file_path)
    
    logger.info(f"Loaded {len(df)} rows from CSV")
    
    # Return just the DataFrame
    return df


@asset(
    group_name="raw_data",
    description="Load raw program master data from Excel",
)
def raw_program_master() -> pd.DataFrame:
    """Load program master information from Excel file.
    
    Returns:
        DataFrame with program metadata.
    """
    file_path = DATA_DIR / "1503_program_master.xlsx"
    
    logger.info(f"Loading program master from {file_path}")
    
    df = pd.read_excel(file_path)
    
    logger.info(f"Loaded {len(df)} programs from master file")
    
    # Return just the DataFrame
    return df


@asset(
    group_name="raw_data",
    description="Load discipline categorization data from Excel",
)
def raw_discipline() -> pd.DataFrame:
    """Load discipline/specialty categorization from Excel file.
    
    Returns:
        DataFrame with discipline information.
    """
    file_path = DATA_DIR / "1503_discipline.xlsx"
    
    logger.info(f"Loading discipline data from {file_path}")
    
    df = pd.read_excel(file_path)
    
    logger.info(f"Loaded {len(df)} discipline records")
    
    # Return just the DataFrame
    return df


# Export all raw data assets
raw_data_assets = [
    raw_program_descriptions_json,
    raw_program_descriptions_csv,
    raw_program_master,
    raw_discipline,
]
