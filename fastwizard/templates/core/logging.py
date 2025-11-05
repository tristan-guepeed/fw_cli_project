"""Template de logging de base."""
def get_template(config):
    return """# app/core/logging.py
import logging
import sys
from pydantic_settings import BaseSettings
from rich.logging import RichHandler
from rich.console import Console


class LoggingSettings(BaseSettings):
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "rich"  # "plain", "json" ou "rich"

    class Config:
        env_prefix = "LOG_"
        env_file = ".env"
        env_file_encoding = "utf-8"


def setup_logging():
    settings = LoggingSettings()
    log_level = settings.LOG_LEVEL.upper()

    # --- Crée le handler selon le format ---
    if settings.LOG_FORMAT == "json":
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(
            logging.Formatter(
                '{"time": "%(asctime)s", "level": "%(levelname)s", "name": "%(name)s", "msg": "%(message)s"}'
            )
        )
    elif settings.LOG_FORMAT == "plain":
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(
            logging.Formatter(
                "[%(asctime)s] [%(levelname)s] %(name)s - %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
        )
    else:
        # Configuration Rich simple
        console = Console()
        console._force_terminal = True  # Force les couleurs dans Docker
        
        handler = RichHandler(
            console=console,
            rich_tracebacks=True,
            markup=True,
            log_time_format="[%H:%M:%S]",
            show_path=False,
            show_level=True,
            tracebacks_show_locals=False,
        )

    # --- Configure le root logger ---
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.handlers = [handler]

    # --- Réduction du bruit SQLAlchemy ---
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.pool").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.orm").setLevel(logging.WARNING)

    # --- Remplace les logs Uvicorn ---
    logging.getLogger("uvicorn.access").handlers = [handler]
    logging.getLogger("uvicorn.access").setLevel(log_level)
    logging.getLogger("uvicorn.error").handlers = [handler]

    # Log de démarrage simple
    logging.getLogger(__name__).info("✅ Logging Rich activé")
"""
