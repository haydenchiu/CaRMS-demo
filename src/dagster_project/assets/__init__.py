"""Dagster assets for the CaRMS data pipeline."""

from .raw_data import raw_data_assets
from .staging import staging_assets
from .serving import serving_assets
from .analytics import analytics_assets

# Combine all assets
all_assets = [
    *raw_data_assets,
    *staging_assets,
    *serving_assets,
    *analytics_assets,
]

__all__ = [
    "raw_data_assets",
    "staging_assets",
    "serving_assets",
    "analytics_assets",
    "all_assets",
]
