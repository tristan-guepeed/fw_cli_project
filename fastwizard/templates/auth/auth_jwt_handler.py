"""Template pour la gestion des tokens JWT"""
def get_template(config):
    secret_key = config.get("secret_key", "your-secret-key-here")
    algorithm = config.get("algorithm", "HS256")
    access_token_expire_minutes = config.get("access_token_expire_minutes", 30)
    refresh_token_expire_days = config.get("refresh_token_expire_days", 7)
    
    return f'''from datetime import datetime, timedelta
from typing import Optional, Union
from jose import JWTError, jwt
import bcrypt
import os
from dotenv import load_dotenv

load_dotenv()

# Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "{secret_key}")
ALGORITHM = "{algorithm}"
ACCESS_TOKEN_EXPIRE_MINUTES = {access_token_expire_minutes}
REFRESH_TOKEN_EXPIRE_DAYS = {refresh_token_expire_days}

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Vérifie un mot de passe contre son hash"""
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def get_password_hash(password: str) -> str:
    """Génère un hash pour un mot de passe"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Crée un token d'accès JWT"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({{"exp": expire, "type": "access"}})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: dict) -> str:
    """Crée un token de rafraîchissement JWT"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({{"exp": expire, "type": "refresh"}})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str, token_type: str = "access") -> Optional[dict]:
    """Vérifie et décode un token JWT"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") != token_type:
            return None
        return payload
    except JWTError:
        return None

def create_token_pair(user_id: int, username: str) -> dict:
    """Crée une paire de tokens (access + refresh)"""
    access_token = create_access_token(data={{"sub": str(user_id), "username": username}})
    refresh_token = create_refresh_token(data={{"sub": str(user_id), "username": username}})
    
    return {{
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }}
'''