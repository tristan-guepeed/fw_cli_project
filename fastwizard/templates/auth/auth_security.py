"""Template pour la configuration de sécurité"""
def get_template(config):
    secret_key = config.get("secret_key", "your-secret-key-here")
    algorithm = config.get("algorithm", "HS256")
    access_token_expire_minutes = config.get("access_token_expire_minutes", 30)
    refresh_token_expire_days = config.get("refresh_token_expire_days", 7)
    
    return f'''from datetime import timedelta
import os
from dotenv import load_dotenv

load_dotenv()

# Configuration de sécurité
SECRET_KEY = os.getenv("SECRET_KEY", "{secret_key}")
ALGORITHM = "{algorithm}"

# Durées d'expiration des tokens
ACCESS_TOKEN_EXPIRE_MINUTES = {access_token_expire_minutes}
REFRESH_TOKEN_EXPIRE_DAYS = {refresh_token_expire_days}

# Configuration des mots de passe
PASSWORD_MIN_LENGTH = 8
PASSWORD_REQUIRE_UPPERCASE = True
PASSWORD_REQUIRE_LOWERCASE = True
PASSWORD_REQUIRE_NUMBERS = True
PASSWORD_REQUIRE_SPECIAL_CHARS = False

# Configuration des cookies sécurisés
COOKIE_SECURE = os.getenv("COOKIE_SECURE", "False").lower() == "true"
COOKIE_HTTP_ONLY = True
COOKIE_SAME_SITE = "lax"

# Rate limiting (requêtes par minute)
RATE_LIMIT_PER_MINUTE = 60

# Configuration des tentatives de connexion
MAX_LOGIN_ATTEMPTS = 5
LOGIN_LOCKOUT_DURATION_MINUTES = 15

# Configuration des sessions
SESSION_TIMEOUT_MINUTES = 30
'''