"""Logging configuration using Loguru and structlog with correlation ID."""
import sys
import json
from pathlib import Path
from loguru import logger
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    app_name: str = "FastAPI Logging Demo"
    debug: bool = False
    log_level: str = "INFO"
    log_dir: Path = Path("logs")

    model_config = {"env_file": ".env"}


settings = Settings()


def setup_logging() -> None:
    """Configure Loguru with both console and file handlers."""
    # Remove default handler
    logger.remove()

    # Ensure logs directory exists
    settings.log_dir.mkdir(exist_ok=True)

    # Console handler with colored output and correlation ID
    logger.add(
        sys.stdout,
        format="<level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
        "<level>{message}</level>",
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

    # Structured JSON logs for processing with correlation ID

    logger.add(
        settings.log_dir / "structured.json",
        format="{message}",
        level=settings.log_level,
        rotation="100 MB",
        retention="10 days",
        compression="zip",
        serialize=False,
    )

    # Add a separate custom JSON handler using json_formatter
    def json_sink(message):
        """Sink for JSON formatted messages."""
        record = message.record
        try:
            correlation_id = record["extra"].get("correlation_id", "N/A")
            # Filter extra dict to exclude correlation_id and request_id
            extra_fields = {k: v for k, v in record["extra"].items() if k not in ("correlation_id", "request_id")}

            log_entry = {
                "timestamp": record["time"].isoformat(),
                "level": record["level"].name,
                "logger": record["name"],
                "function": record["function"],
                "line": record["line"],
                "message": record["message"],
                "correlation_id": correlation_id,
            }

            # Add extra fields if present
            if extra_fields:
                log_entry["extra"] = extra_fields

            with open(settings.log_dir / "structured.json", "a") as f:
                f.write(json.dumps(log_entry) + "\n")
        except Exception:
            pass  # Silently ignore formatting errors

    logger.add(
        json_sink,
        level=settings.log_level,
    )


# Initialize logging on module import
setup_logging()
