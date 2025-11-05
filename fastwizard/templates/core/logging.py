"""Template de logging de base."""
def get_template(config):
    return """# app/core/logging.py
import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler
from pydantic_settings import BaseSettings
from rich.logging import RichHandler
from rich.console import Console
from typing import Literal


class LoggingSettings(BaseSettings):
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: Literal["plain", "json", "rich"] = "rich"  # "plain", "json", "rich"
    LOG_FILE: str = "logs/app.log"
    LOG_MAX_BYTES: int = 10_000_000  # 10 MB
    LOG_BACKUP_COUNT: int = 5

    class Config:
        env_prefix = "LOG_"
        env_file = ".env"
        env_file_encoding = "utf-8"


def setup_logging():
    settings = LoggingSettings()
    log_level = settings.LOG_LEVEL.upper()

    # --- Crée le dossier de log si nécessaire ---
    log_path = Path(settings.LOG_FILE)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    # --- File handler avec rotation ---
    file_formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] %(name)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    file_handler = RotatingFileHandler(
        settings.LOG_FILE,
        maxBytes=settings.LOG_MAX_BYTES,
        backupCount=settings.LOG_BACKUP_COUNT,
        encoding="utf-8"
    )
    file_handler.setLevel(log_level)
    file_handler.setFormatter(file_formatter)

    # --- Stream handler pour la console ---
    if settings.LOG_FORMAT == "json":
        stream_formatter = logging.Formatter(
            '{"time": "%(asctime)s", "level": "%(levelname)s", "logger": "%(name)s", "msg": "%(message)s"}'
        )
        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setLevel(log_level)
        stream_handler.setFormatter(stream_formatter)
    elif settings.LOG_FORMAT == "plain":
        stream_formatter = logging.Formatter(
            "[%(asctime)s] [%(levelname)s] %(name)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setLevel(log_level)
        stream_handler.setFormatter(stream_formatter)
    else:
        console = Console()
        console._force_terminal = True  # pour Docker
        stream_handler = RichHandler(
            console=console,
            rich_tracebacks=True,
            markup=True,
            log_time_format="[%H:%M:%S]",
            show_path=False,
            show_level=True,
            tracebacks_show_locals=False,
        )
        stream_handler.setLevel(log_level)

    # --- Configure le root logger ---
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.handlers = [stream_handler, file_handler]
    root_logger.propagate = True

    # --- Réduction du bruit SQLAlchemy ---
    logging.getLogger("sqlalchemy").setLevel(logging.WARNING)

    # --- Remplace les logs Uvicorn ---
    for name in ("uvicorn.access", "uvicorn.error"):
        logger = logging.getLogger(name)
        logger.handlers = [stream_handler, file_handler]
        logger.setLevel(log_level)

    # --- Log de démarrage ---
    logging.getLogger(__name__).info("✅ Logging initialized: console + file")

"""
