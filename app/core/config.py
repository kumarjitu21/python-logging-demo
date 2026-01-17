"""Configuration settings for the application."""
from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    """Application settings."""
    
    app_name: str = "FastAPI Logging Demo"
    debug: bool = False
    log_level: str = "INFO"
    log_dir: Path = Path("logs")
    version: str = "0.1.0"
    
    model_config = {"env_file": ".env"}


settings = Settings()
