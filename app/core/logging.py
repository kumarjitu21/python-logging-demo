"""Logging configuration using Loguru and structlog."""
import sys
import json
from pathlib import Path
from typing import Any
from loguru import logger
from pythonjsonlogger import jsonlogger
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""
    
    app_name: str = "FastAPI Logging Demo"
    debug: bool = False
    log_level: str = "INFO"
    log_dir: Path = Path("logs")
    
    model_config = {"env_file": ".env"}


settings = Settings()


class CustomJsonFormatter(jsonlogger.JsonFormatter):
    """Custom JSON formatter for structured logging."""
    
    def add_fields(self, log_record: dict, record: Any, message_dict: dict) -> None:
        """Add custom fields to log record."""
        super().add_fields(log_record, record, message_dict)
        log_record['timestamp'] = record.created
        log_record['level'] = record.levelname
        log_record['module'] = record.module
        log_record['function'] = record.funcName
        log_record['line'] = record.lineno


def setup_logging() -> None:
    """Configure Loguru with both console and file handlers."""
    # Remove default handler
    logger.remove()
    
    # Ensure logs directory exists
    settings.log_dir.mkdir(exist_ok=True)
    
    # Console handler with colored output
    logger.add(
        sys.stdout,
        format="<level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=settings.log_level,
        colorize=True,
    )
    
    # File handler with rotation - General logs
    logger.add(
        settings.log_dir / "app.log",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level=settings.log_level,
        rotation="100 MB",
        retention="10 days",
        compression="zip",
        backtrace=True,
        diagnose=True,
    )
    
    # File handler for errors only
    logger.add(
        settings.log_dir / "errors.log",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level="ERROR",
        rotation="50 MB",
        retention="30 days",
        compression="zip",
        backtrace=True,
        diagnose=True,
    )
    
    # Structured JSON logs for processing
    def json_formatter(record):
        """Format log record as JSON."""
        return json.dumps({
            "timestamp": record["time"].isoformat(),
            "level": record["level"].name,
            "logger": record["name"],
            "function": record["function"],
            "line": record["line"],
            "message": record["message"],
            "extra": record["extra"],
        })
    
    logger.add(
        settings.log_dir / "structured.json",
        format=json_formatter,
        level=settings.log_level,
        rotation="100 MB",
        retention="10 days",
        compression="zip",
    )


# Initialize logging on module import
setup_logging()
