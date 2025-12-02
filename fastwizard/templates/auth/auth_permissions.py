def get_template(config):
    return '''from typing import Optional, Callable, Any
from fastapi import Depends, HTTPException, status
from fastapi import Path
from sqlalchemy.orm import Session

from app.domains.auth.dependencies import get_current_active_user
from app.domains.auth.model import User
from app.database import get_db


def require_admin(current_user: User = Depends(get_current_active_user)) -> User:
    """Dépendance qui exige que l'utilisateur soit administrateur."""
    if current_user.role.name != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Droits d'administrateur requis"
        )
    return current_user


def require_self_or_admin_by_param(
    user_id: int = Path(..., description="ID de l'utilisateur cible"),
    current_user: User = Depends(get_current_active_user),
) -> User:
    """Autorise si l'utilisateur courant est admin ou correspond à l'ID en paramètre de route."""
    if current_user.role.name == "admin" or current_user.id == user_id:
        return current_user
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Accès refusé : réservée au propriétaire de la ressource ou à un admin"
    )


def require_self_or_admin_by_owner(
    owner_id: int,
    current_user: User = Depends(get_current_active_user),
) -> User:
    """
    Vérifie à l'intérieur d'une route/service que l'utilisateur courant est admin
    ou propriétaire de la ressource (owner_id).
    Usage : appelez cette fonction dans la route après avoir chargé la ressource.
    """
    if current_user.role.name == "admin" or current_user.id == owner_id:
        return current_user
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Accès refusé : réservée au propriétaire de la ressource ou à un admin"
    )
'''
