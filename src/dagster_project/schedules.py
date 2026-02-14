"""Dagster schedules for automated pipeline runs."""

from dagster import schedule, ScheduleDefinition, RunRequest, SkipReason, DefaultScheduleStatus


@schedule(
    cron_schedule="0 2 * * *",  # Run at 2 AM daily
    job_name="daily_etl_pipeline",
    default_status=DefaultScheduleStatus.STOPPED,
)
def daily_etl_schedule():
    """Run the complete ETL pipeline daily.
    
    Processes raw data through staging, serving, and analytics layers.
    """
    return RunRequest(
        run_config={},
        tags={"schedule": "daily", "pipeline": "etl"},
    )


@schedule(
    cron_schedule="0 */6 * * *",  # Run every 6 hours
    job_name="analytics_refresh",
    default_status=DefaultScheduleStatus.STOPPED,
)
def analytics_refresh_schedule():
    """Refresh analytics tables every 6 hours.
    
    Updates analytical aggregations without full ETL run.
    """
    return RunRequest(
        run_config={},
        tags={"schedule": "periodic", "pipeline": "analytics"},
    )


# Export schedules
all_schedules = [
    daily_etl_schedule,
    analytics_refresh_schedule,
]
