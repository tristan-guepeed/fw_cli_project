"""Template pour le service OAuth"""
def get_template(config):
    return f'''
import httpx
from .oauth_provider import PROVIDER, AUTH_URL, TOKEN_URL, USER_INFO_URL, CLIENT_ID, CLIENT_SECRET, REDIRECT_URI
# app/domains/auth/services/oauth_service.py

from sqlalchemy.orm import Session
from app.domains.auth.model import User
from app.core.security import get_password_hash
from datetime import datetime
import secrets

async def get_or_create_oauth_user(email: str, name: str, provider: str, db: Session):
    """Trouve ou crée un utilisateur lié à OAuth"""

    user = db.query(User).filter(User.email == email).first()

    if user:
        return user  # déjà existant → login normal

    # Sinon, création
    random_password = secrets.token_hex(32)

    new_user = User(
        email=email,
        username=name.replace(" ", "").lower(),
        full_name=name,
        hashed_password=get_password_hash(random_password),
        is_active=True,
        oauth_provider=provider,
        oauth_account_created_at=datetime.utcnow()
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

async def get_access_token(code: str) -> dict:
    """
    Échange le code OAuth contre un access token.
    """
    async with httpx.AsyncClient() as client:
        response = await client.post(
            TOKEN_URL,
            data={{
                "grant_type": "authorization_code",
                "code": code,
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET,
                "redirect_uri": REDIRECT_URI
            }},
            headers={{"Accept": "application/json"}}
        )
        response.raise_for_status()
        return response.json()

async def get_user_info(access_token: str) -> dict:
    """
    Récupère les informations de l'utilisateur depuis le provider.
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(
            USER_INFO_URL,
            headers={{"Authorization": f"Bearer {{access_token}}" }}
        )
        response.raise_for_status()
        return response.json()
'''
