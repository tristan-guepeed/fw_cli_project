"""Template pour les routes d'authentification"""
def get_template(config):
    return '''from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.user import User
from app.schemas.auth import (
    UserCreate, UserResponse, UserLogin, Token, TokenRefresh, 
    PasswordChange, UserUpdate
)
from app.auth.jwt_handler import (
    verify_password, get_password_hash, create_token_pair, 
    verify_token
)
from app.auth.dependencies import get_current_active_user, get_current_admin_user

router = APIRouter()

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    """Enregistre un nouvel utilisateur"""
    
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

@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Connecte un utilisateur et retourne les tokens"""
    
    # Vérifier les identifiants
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Nom d'utilisateur ou mot de passe incorrect",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Compte utilisateur inactif"
        )
    
    # Créer les tokens
    tokens = create_token_pair(user.id, user.username)
    return tokens

@router.post("/refresh", response_model=Token)
async def refresh_token(token_data: TokenRefresh, db: Session = Depends(get_db)):
    """Rafraîchit un token d'accès avec un token de rafraîchissement"""
    
    # Vérifier le token de rafraîchissement
    payload = verify_token(token_data.refresh_token, "refresh")
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de rafraîchissement invalide ou expiré"
        )
    
    # Récupérer l'utilisateur
    user_id = payload.get("sub")
    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Utilisateur non trouvé ou inactif"
        )
    
    # Créer de nouveaux tokens
    tokens = create_token_pair(user.id, user.username)
    return tokens

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
    
    # Mettre à jour les champs
    update_data = user_update.dict(exclude_unset=True)
    if "password" in update_data:
        update_data["hashed_password"] = get_password_hash(update_data.pop("password"))
    
    for field, value in update_data.items():
        setattr(current_user, field, value)
    
    db.commit()
    db.refresh(current_user)
    
    return current_user

@router.post("/change-password")
async def change_password(
    password_change: PasswordChange,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
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

@router.get("/users", response_model=List[UserResponse])
async def get_all_users(
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Récupère la liste de tous les utilisateurs (admin seulement)"""
    users = db.query(User).all()
    return users

@router.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Supprime un utilisateur (admin seulement)"""
    
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Vous ne pouvez pas supprimer votre propre compte"
        )
    
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