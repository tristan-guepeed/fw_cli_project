"""Template pour le service OAuth multi-provider"""
def get_template(config):
    return f'''
import httpx
from sqlalchemy.orm import Session
from app.domains.auth.model import User
from app.domains.auth.jwt_handler import get_password_hash
from datetime import datetime
import secrets
from .oauth_provider import PROVIDER, AUTH_URL, TOKEN_URL, USER_INFO_URL, CLIENT_ID, CLIENT_SECRET, REDIRECT_URI

async def get_or_create_oauth_user(email: str, username: str, provider: str, oauth_id: str, db: Session):
    """Trouve ou crée un utilisateur lié à OAuth (Google ou GitHub)"""

    user = db.query(User).filter(User.email == email).first()
    if user:
        return user

    random_password = secrets.token_hex(32)
    user_kwargs = {{
        "email": email,
        "username": username,
        "hashed_password": get_password_hash(random_password),
        "is_active": True,
        "oauth_provider": provider,
        "oauth_account_created_at": datetime.utcnow()
    }}

    if provider.lower() == "google":
        user_kwargs["google_id"] = oauth_id
    elif provider.lower() == "github":
        user_kwargs["github_id"] = oauth_id

    new_user = User(**user_kwargs)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

async def get_access_token(code: str) -> dict:
    """Échange le code OAuth contre un access token"""
    async with httpx.AsyncClient() as client:
        resp = await client.post(
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
        resp.raise_for_status()
        return resp.json()

async def get_user_info(access_token: str) -> dict:
    """Récupère les informations de l'utilisateur depuis le provider"""
    async with httpx.AsyncClient() as client:
        user_info = {{}}

        if PROVIDER.lower() == "github":
            # Infos de base
            resp = await client.get(
                "https://api.github.com/user",
                headers={{"Authorization": f"Bearer {{access_token}}" }}
            )
            resp.raise_for_status()
            user_info = resp.json()

            # Emails
            email_resp = await client.get(
                "https://api.github.com/user/emails",
                headers={{"Authorization": f"Bearer {{access_token}}" }}
            )
            email_resp.raise_for_status()
            emails = email_resp.json()
            primary_email = next((e["email"] for e in emails if e.get("primary") and e.get("verified")), None)
            user_info["email"] = primary_email

        else:
            # Google ou autres providers
            resp = await client.get(
                USER_INFO_URL,
                headers={{"Authorization": f"Bearer {{access_token}}" }}
            )
            resp.raise_for_status()
            user_info = resp.json()

    return user_info
'''
