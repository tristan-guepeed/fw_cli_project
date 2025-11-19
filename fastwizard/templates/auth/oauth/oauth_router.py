"""Template pour le router OAuth"""
def get_template(config):
    return f'''
from fastapi import APIRouter, HTTPException, Depends
import requests
from app.domains.auth.jwt_handler import create_token_pair
from .oauth_provider import CLIENT_ID
from .oauth_provider import CLIENT_SECRET
from .oauth_provider import REDIRECT_URI
from .oauth_provider import AUTH_URL
from sqlalchemy.orm import Session
from app.database import get_db
from app.domains.auth.services import get_user_by_email, create_user_google
router = APIRouter()

@router.get("/login")
async def oauth_login():
    """
    Redirige l'utilisateur vers le provider OAuth pour se connecter.
    """
    return {{
        "auth_url": f"{{AUTH_URL}}?client_id={{CLIENT_ID}}&redirect_uri={{REDIRECT_URI}}&response_type=code&scope=openid email profile"
    }}

@router.get("/callback")
async def google_callback(code: str, db: Session = Depends(get_db)):
    token_res = requests.post(
        "https://oauth2.googleapis.com/token",
        data={{
            "code": code,
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "redirect_uri": REDIRECT_URI,
            "grant_type": "authorization_code",
        }},
    )

    token_data = token_res.json()

    if "access_token" not in token_data:
        raise HTTPException(status_code=400, detail="Invalid Google token")

    user_info = requests.get(
        "https://www.googleapis.com/oauth2/v3/userinfo",
        headers={{"Authorization": f"Bearer {{token_data['access_token']}}"}}
    ).json()

    email = user_info.get("email")
    google_id = user_info.get("sub")

    if not email:
        raise HTTPException(status_code=400, detail="Google email not available")

    user = get_user_by_email(db, email=email)

    if not user:
        user = create_user_google(db, email=email, google_id=google_id)

    tokens = create_token_pair(user_id=user.id, username=user.username)

    return tokens

'''
