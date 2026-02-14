"""Dagster job definitions for orchestrating assets."""

from dagster import define_asset_job, AssetSelection

# Define job for complete ETL pipeline
daily_etl_pipeline = define_asset_job(
    name="daily_etl_pipeline",
    description="Complete ETL pipeline from raw data to analytics",
    selection=AssetSelection.all(),
    tags={"pipeline": "full_etl"},
)

# Define job for analytics refresh only
analytics_refresh = define_asset_job(
    name="analytics_refresh",
    description="Refresh analytics tables only",
    selection=AssetSelection.groups("analytics"),
    tags={"pipeline": "analytics_only"},
)

# Define job for serving layer only (load warehouse)
warehouse_load = define_asset_job(
    name="warehouse_load",
    description="Load data warehouse (serving layer)",
    selection=AssetSelection.groups("serving"),
    tags={"pipeline": "warehouse"},
)

# Define job for staging transformations
staging_transform = define_asset_job(
    name="staging_transform",
    description="Run staging transformations",
    selection=AssetSelection.groups("staging"),
    tags={"pipeline": "staging"},
)

# Export all jobs
all_jobs = [
    daily_etl_pipeline,
    analytics_refresh,
    warehouse_load,
    staging_transform,
]
