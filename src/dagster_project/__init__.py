"""Dagster project for CaRMS data pipeline."""

from dagster import Definitions
from .assets import all_assets
from .assets.data_quality import data_quality_checks
from .resources import resource_defs
from .schedules import all_schedules
from .jobs import all_jobs

# Define all assets, resources, schedules, and jobs
defs = Definitions(
    assets=all_assets,
    asset_checks=data_quality_checks,
    resources=resource_defs,
    schedules=all_schedules,
    jobs=all_jobs,
)
