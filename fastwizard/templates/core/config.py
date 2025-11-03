"""Template pour la configuration centralisée de l'application"""

def get_template(config):
    app_name = config.get("app_name", "Mon Projet FastAPI")

    return f'''"""
Configuration centralisée de l'application FastAPI
Toutes les valeurs proviennent du fichier .env ou de valeurs par défaut.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
from typing import List

class Settings(BaseSettings):
    # --- Application ---
    APP_NAME: str = "{app_name}"
    DEBUG: bool = True
    ENVIRONMENT: str = "development"

    # --- Sécurité / JWT ---
    SECRET_KEY: str = "your-secret-key-here-change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # --- Mots de passe ---
    PASSWORD_MIN_LENGTH: int = 8
    PASSWORD_REQUIRE_UPPERCASE: bool = True
    PASSWORD_REQUIRE_LOWERCASE: bool = True
    PASSWORD_REQUIRE_NUMBERS: bool = True
    PASSWORD_REQUIRE_SPECIAL_CHARS: bool = False

    # --- Cookies ---
    COOKIE_SECURE: bool = False
    COOKIE_HTTP_ONLY: bool = True
    COOKIE_SAME_SITE: str = "lax"

    # --- Sécurité additionnelle ---
    RATE_LIMIT_PER_MINUTE: int = 60
    MAX_LOGIN_ATTEMPTS: int = 5
    LOGIN_LOCKOUT_DURATION_MINUTES: int = 15
    SESSION_TIMEOUT_MINUTES: int = 30

    # --- CORS ---
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:8080",
        "http://localhost:4200",
    ]
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: List[str] = ["*"]
    CORS_ALLOW_HEADERS: List[str] = ["*"]

    # --- Base de données ---
    DATABASE_URL: str | None = None

    # --- Configuration du modèle ---
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )

@lru_cache()
def get_settings() -> Settings:
    """Renvoie une instance unique de Settings (cache pour éviter les recharges)"""
    return Settings()
'''
