"""Template pour les routes d'authentification"""
def get_template(config):
    return '''from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.domains.auth.dependencies import get_current_active_user
from typing import List
from app.database import get_db
from app.domains.auth.model import User
from app.domains.auth.schemas import (
    UserCreate, UserResponse, Token, TokenRefresh, 
    PasswordChange, UserUpdate
)
from app.domains.auth.dependencies import get_current_active_user, get_current_admin_user
from app.domains.auth.services import register_user_service, login_user_service, refresh_token_service, update_current_user_service, change_password_service, delete_user_service, create_role, get_roles, get_role, update_role, delete_role
from app.domains.auth.schemas import RoleCreate, RoleUpdate, RoleResponse

router = APIRouter()

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    """Route d'enregistrement d'un utilisateur"""
    return await register_user_service(user, db)

@router.post("/login", response_model=Token, status_code=status.HTTP_200_OK)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """Connecte un utilisateur et retourne les tokens"""
    return await login_user_service(form_data, db)

@router.post("/refresh", response_model=Token, status_code=status.HTTP_200_OK)
async def refresh_token(token_data: TokenRefresh, db: Session = Depends(get_db)):
    """Rafraîchit un token d'accès avec un token de rafraîchissement"""
    return await refresh_token_service(token_data, db)

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_active_user)):
    """Récupère les informations de l'utilisateur actuel"""
    return current_user

@router.put("/me", response_model=UserResponse)
async def update_current_user(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Met à jour les informations de l'utilisateur actuel"""
    return await update_current_user_service(user_update, current_user, db)

@router.post("/change-password", status_code=status.HTTP_200_OK)
async def change_password(
    password_change: PasswordChange,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Change le mot de passe de l'utilisateur actuel"""
    return await change_password_service(password_change, current_user, db)

@router.get("/users", response_model=List[UserResponse])
async def get_all_users(
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Récupère la liste de tous les utilisateurs (admin seulement)"""
    users = db.query(User).all()
    return users

@router.delete("/users/{user_id}", status_code=status.HTTP_200_OK)
async def delete_user(
    user_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Supprime un utilisateur (admin seulement)."""
    return await delete_user_service(user_id, current_user, db)

@router.post("/roles/", response_model=RoleResponse)
def api_create_role(role: RoleCreate, db: Session = Depends(get_db), current_user : User = Depends(get_current_admin_user)):
    return create_role(db, role)

@router.get("/roles/", response_model=list[RoleResponse])
def api_get_roles(db: Session = Depends(get_db)):
    return get_roles(db)

@router.get("/roles/{role_id}", response_model=RoleResponse)
def api_get_role(role_id: int, db: Session = Depends(get_db)):
    return get_role(db, role_id)

@router.put("/roles/{role_id}", response_model=RoleResponse)
def api_update_role(role_id: int, role: RoleUpdate, db: Session = Depends(get_db), current_user : User = Depends(get_current_admin_user)):
    return update_role(db, role_id, role)

@router.delete("/roles/{role_id}")
def api_delete_role(role_id: int, db: Session = Depends(get_db), current_user : User = Depends(get_current_admin_user)):
    return delete_role(db, role_id)
'''