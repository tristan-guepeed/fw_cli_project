"""Template pour les services d'authentification"""
def get_template(config):
    selected_modules = config.get("selected_modules", [])
    oauth_module = next((m for m in selected_modules if m.startswith("auth-oauth")), None)

    if oauth_module == "auth-oauth-google" or oauth_module == "auth-oauth-github":
        oauth_functions = '''def get_user_by_email(db, email: str):
    return db.query(User).filter(User.email == email).first()


def create_user_google(db, email: str, google_id: str):
    fake_password = secrets.token_urlsafe(32)  # mot de passe aléatoire
    hashed_password = get_password_hash(fake_password)
    user = User(
        username=email.split("@")[0],
        email=email,
        hashed_password=hashed_password,
        google_id=google_id,
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
''' 
    else:
        oauth_functions = ""



    template='''from fastapi import APIRouter, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List
from app.domains.auth.model import User
from app.domains.auth.schemas import (
    UserCreate, UserResponse, Token, TokenRefresh, 
    PasswordChange, UserUpdate
)
import secrets
from app.domains.auth.jwt_handler import (
    verify_password, get_password_hash, create_token_pair, 
    verify_token
)

async def register_user_service(user: UserCreate, db: Session) -> UserResponse:
    """Logique d'enregistrement d'un nouvel utilisateur"""

    # Vérifier si l'utilisateur existe déjà
    if db.query(User).filter(User.username == user.username).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Le nom d'utilisateur est déjà utilisé"
        )

    if db.query(User).filter(User.email == user.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="L'email est déjà utilisé"
        )

    # Créer le nouvel utilisateur
    hashed_password = get_password_hash(user.password)
    db_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user

async def login_user_service(form_data: OAuth2PasswordRequestForm, db: Session) -> Token:
    """Authentifie un utilisateur et retourne ses tokens"""

    # Vérifier les identifiants
    user = db.query(User).filter(User.username == form_data.username).first()

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Nom d'utilisateur ou mot de passe incorrect",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Vérifier si le compte est actif
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Compte utilisateur inactif"
        )

    # Générer le couple de tokens (access + refresh)
    tokens = create_token_pair(user.id, user.username)
    return tokens

async def refresh_token_service(token_data: TokenRefresh, db: Session) -> Token:
    """Rafraîchit un token d'accès avec un token de rafraîchissement"""

    # Vérifier le token de rafraîchissement
    payload = verify_token(token_data.refresh_token, "refresh")
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de rafraîchissement invalide ou expiré"
        )

    # Extraire l'ID utilisateur du payload
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalide : identifiant utilisateur manquant"
        )

    # Récupérer l'utilisateur
    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Utilisateur non trouvé ou inactif"
        )

    # Générer un nouveau couple de tokens
    tokens = create_token_pair(user.id, user.username)
    return tokens

async def update_current_user_service(
    user_update: UserUpdate,
    current_user: User,
    db: Session
) -> UserResponse:
    """Met à jour les informations du profil utilisateur"""

    # Vérifier les conflits d'username
    if user_update.username and user_update.username != current_user.username:
        if db.query(User).filter(User.username == user_update.username).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Le nom d'utilisateur est déjà utilisé"
            )

    # Vérifier les conflits d'email
    if user_update.email and user_update.email != current_user.email:
        if db.query(User).filter(User.email == user_update.email).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="L'email est déjà utilisé"
            )

    # Préparer les données à mettre à jour
    update_data = user_update.dict(exclude_unset=True)

    # Si le mot de passe est présent, le hacher
    if "password" in update_data:
        update_data["hashed_password"] = get_password_hash(update_data.pop("password"))

    # Appliquer les modifications
    for field, value in update_data.items():
        setattr(current_user, field, value)

    db.commit()
    db.refresh(current_user)

    return current_user

async def change_password_service(
    password_change: PasswordChange,
    current_user: User,
    db: Session
) -> dict:
    """Change le mot de passe de l'utilisateur actuel"""

    # Vérifier le mot de passe actuel
    if not verify_password(password_change.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mot de passe actuel incorrect"
        )

    # Mettre à jour le mot de passe
    current_user.hashed_password = get_password_hash(password_change.new_password)
    db.commit()

    return {"message": "Mot de passe modifié avec succès"}

async def delete_user_service(user_id: int, current_user: User, db: Session) -> dict:
    """Supprime un utilisateur (réservé aux administrateurs)."""

    # Empêche la suppression de son propre compte
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Vous ne pouvez pas supprimer votre propre compte"
        )

    # Recherche de l'utilisateur à supprimer
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utilisateur non trouvé"
        )

    db.delete(user)
    db.commit()

    return {"message": "Utilisateur supprimé avec succès"}
'''

    return template + oauth_functions