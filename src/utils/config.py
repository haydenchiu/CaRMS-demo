"""Configuration management using pydantic-settings."""

from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Database
    database_url: str = "postgresql://carms:carms@localhost:5434/carms"
    
    # OpenAI (for embeddings)
    openai_api_key: Optional[str] = None
    
    # Application
    environment: str = "development"  # development, staging, production
    log_level: str = "INFO"
    debug: bool = False
    
    # Dagster
    dagster_home: str = "/opt/dagster/dagster_home"
    
    # Data paths
    data_dir: str = "data"
    
    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_reload: bool = True


# Global settings instance
settings = Settings()
