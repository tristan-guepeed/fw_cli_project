"""Template pour la configuration de sécurité"""

def get_template(config):
    return '''"""
Paramètres de sécurité centralisés
Toutes les valeurs proviennent de app.core.config.Settings
"""

from datetime import timedelta
from app.core.config import get_settings

settings = get_settings()

# --- JWT ---
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES
REFRESH_TOKEN_EXPIRE_DAYS = settings.REFRESH_TOKEN_EXPIRE_DAYS

# --- Mot de passe ---
PASSWORD_MIN_LENGTH = settings.PASSWORD_MIN_LENGTH
PASSWORD_REQUIRE_UPPERCASE = settings.PASSWORD_REQUIRE_UPPERCASE
PASSWORD_REQUIRE_LOWERCASE = settings.PASSWORD_REQUIRE_LOWERCASE
PASSWORD_REQUIRE_NUMBERS = settings.PASSWORD_REQUIRE_NUMBERS
PASSWORD_REQUIRE_SPECIAL_CHARS = settings.PASSWORD_REQUIRE_SPECIAL_CHARS

# --- Cookies ---
COOKIE_SECURE = settings.COOKIE_SECURE
COOKIE_HTTP_ONLY = settings.COOKIE_HTTP_ONLY
COOKIE_SAME_SITE = settings.COOKIE_SAME_SITE

# --- Sécurité / sessions ---
RATE_LIMIT_PER_MINUTE = settings.RATE_LIMIT_PER_MINUTE
MAX_LOGIN_ATTEMPTS = settings.MAX_LOGIN_ATTEMPTS
LOGIN_LOCKOUT_DURATION_MINUTES = settings.LOGIN_LOCKOUT_DURATION_MINUTES
SESSION_TIMEOUT_MINUTES = settings.SESSION_TIMEOUT_MINUTES

# --- Helpers ---
ACCESS_TOKEN_EXPIRE = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
REFRESH_TOKEN_EXPIRE = timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
'''
