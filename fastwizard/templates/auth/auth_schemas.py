"""Template pour les schémas Pydantic d'authentification"""
def get_template(config):
    return '''from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    """Schéma de base pour un utilisateur"""
    username: str
    email: EmailStr
    
    @field_validator('username')
    @classmethod
    def username_must_be_valid(cls, v):
        if len(v) < 3:
            raise ValueError("Le nom d'utilisateur doit contenir au moins 3 caractères")
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError("Le nom d'utilisateur ne peut contenir que des lettres, chiffres, tirets et underscores")
        return v

class UserCreate(UserBase):
    """Schéma pour la création d'un utilisateur"""
    password: str
    
    @field_validator('password')
    @classmethod
    def password_must_be_strong(cls, v):
        if len(v) < 8:
            raise ValueError("Le mot de passe doit contenir au moins 8 caractères")
        return v

class UserUpdate(BaseModel):
    """Schéma pour la mise à jour d'un utilisateur"""
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None
    
    @field_validator('username')
    @classmethod
    def username_must_be_valid(cls, v):
        if v is not None:
            if len(v) < 3:
                raise ValueError("Le nom d'utilisateur doit contenir au moins 3 caractères")
            if not v.replace('_', '').replace('-', '').isalnum():
                raise ValueError("Le nom d'utilisateur ne peut contenir que des lettres, chiffres, tirets et underscores")
        return v
    
    @field_validator('password')
    @classmethod
    def password_must_be_strong(cls, v):
        if v is not None and len(v) < 8:
            raise ValueError("Le mot de passe doit contenir au moins 8 caractères")
        return v

class UserResponse(UserBase):
    """Schéma de réponse pour un utilisateur"""
    id: int
    is_active: bool
    is_admin: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    model_config = {"from_attributes": True}

class UserLogin(BaseModel):
    """Schéma pour la connexion d'un utilisateur"""
    username: str
    password: str

class Token(BaseModel):
    """Schéma pour les tokens d'authentification"""
    access_token: str
    refresh_token: str
    token_type: str

class TokenRefresh(BaseModel):
    """Schéma pour le rafraîchissement de token"""
    refresh_token: str

class TokenData(BaseModel):
    """Schéma pour les données du token"""
    sub: Optional[str] = None
    username: Optional[str] = None
    type: Optional[str] = None

class PasswordChange(BaseModel):
    """Schéma pour le changement de mot de passe"""
    current_password: str
    new_password: str
    
    @field_validator('new_password')
    @classmethod
    def new_password_must_be_strong(cls, v):
        if len(v) < 8:
            raise ValueError("Le nouveau mot de passe doit contenir au moins 8 caractères")
        return v

class RoleBase(BaseModel):
    name: str

class RoleCreate(RoleBase):
    pass

class RoleUpdate(RoleBase):
    pass

class RoleResponse(RoleBase):
    id: int

    class Config:
        orm_mode = True

'''