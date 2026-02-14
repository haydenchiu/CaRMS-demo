"""Dagster project for CaRMS data pipeline."""

from dagster import Definitions
from .assets import raw_data_assets, all_assets
from .resources import database_resource, resource_defs

# Define all assets and resources
defs = Definitions(
    assets=all_assets,
    resources=resource_defs,
)
