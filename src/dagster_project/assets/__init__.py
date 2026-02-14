"""Dagster assets for the CaRMS data pipeline."""

from .raw_data import raw_data_assets

# Combine all assets
all_assets = [
    *raw_data_assets,
]

__all__ = [
    "raw_data_assets",
    "all_assets",
]
