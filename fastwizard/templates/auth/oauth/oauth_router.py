"""Template pour le router OAuth multi-provider"""
def get_template(config):
    provider = config.get("provider", "")
    return f'''
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.domains.auth.jwt_handler import create_token_pair
from app.database import get_db
from app.domains.oauth.{provider}.oauth_services import get_or_create_oauth_user
from app.domains.auth.services import get_user_by_email, create_user_google
import requests
import httpx

from .oauth_provider import PROVIDER, CLIENT_ID, CLIENT_SECRET, REDIRECT_URI, AUTH_URL, TOKEN_URL, USER_INFO_URL

router = APIRouter()

@router.get("/login")
async def oauth_login():
    """
    Redirige l'utilisateur vers le provider OAuth pour se connecter.
    """
    scope = "openid email profile"
    if PROVIDER.lower() == "github":
        scope = "read:user user:email"

    return {{
        "auth_url": f"{{AUTH_URL}}?client_id={{CLIENT_ID}}&redirect_uri={{REDIRECT_URI}}&response_type=code&scope={{scope}}"
    }}

@router.get("/callback")
async def oauth_callback(code: str, db: Session = Depends(get_db)):
    """
    Callback OAuth pour Google ou GitHub
    """
    token_data = {{}}

    if PROVIDER.lower() == "google":
        # Échange code → token
        token_res = requests.post(
            TOKEN_URL,
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

        # Récupération des infos utilisateur
        user_info = requests.get(
            USER_INFO_URL,
            headers={{"Authorization": f"Bearer {{token_data['access_token']}}"}}
        ).json()
        email = user_info.get("email")
        oauth_id = user_info.get("sub")
        if not email:
            raise HTTPException(status_code=400, detail="Google email not available")

        user = get_user_by_email(db, email=email)
        if not user:
            user = create_user_google(db, email=email, google_id=oauth_id)

    elif PROVIDER.lower() == "github":
        # Échange code → token
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                TOKEN_URL,
                data={{
                    "code": code,
                    "client_id": CLIENT_ID,
                    "client_secret": CLIENT_SECRET,
                    "redirect_uri": REDIRECT_URI
                }},
                headers={{"Accept": "application/json"}}
            )
            resp.raise_for_status()
            token_data = resp.json()

        access_token = token_data.get("access_token")
        if not access_token:
            raise HTTPException(status_code=400, detail="Invalid GitHub token")

        # Récupération des infos utilisateur
        async with httpx.AsyncClient() as client:
            user_resp = await client.get(
                USER_INFO_URL,
                headers={{"Authorization": f"Bearer {{access_token}}" }}
            )
            user_resp.raise_for_status()
            user_info = user_resp.json()
            username = user_info.get("login")
            github_id = str(user_info.get("id"))

            # Récupération email principal
            email_resp = await client.get(
                "https://api.github.com/user/emails",
                headers={{"Authorization": f"Bearer {{access_token}}" }}
            )
            email_resp.raise_for_status()
            emails = email_resp.json()
            email = next((e["email"] for e in emails if e.get("primary") and e.get("verified")), None)
            if not email:
                raise HTTPException(status_code=400, detail="GitHub email not available")

        # Création/utilisateur OAuth
        user = await get_or_create_oauth_user(
            email=email,
            username=username,
            provider="github",
            oauth_id=github_id,
            db=db
        )

    else:
        raise HTTPException(status_code=400, detail="Unknown OAuth provider")

    # Génération tokens
    tokens = create_token_pair(user_id=user.id, username=user.username)
    return tokens
'''
