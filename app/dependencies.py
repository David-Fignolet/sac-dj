from typing import Generator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from . import models, schemas
from .database import get_db
from .config import settings

# Schéma OAuth2 pour l'authentification par token
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_PREFIX}/auth/login",
    auto_error=False
)

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> models.User:
    """
    Dépendance pour obtenir l'utilisateur actuellement authentifié.
    
    Args:
        token: Le token JWT d'authentification
        db: La session de base de données
        
    Returns:
        L'utilisateur authentifié
        
    Raises:
        HTTPException: Si l'authentification échoue
    """
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentification requise",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Impossible de valider les informations d'identification",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = schemas.TokenData(username=username)
    except (JWTError, ValidationError):
        raise credentials_exception
    
    user = await models.User.get_by_username(db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(
    current_user: models.User = Depends(get_current_user),
) -> models.User:
    """
    Vérifie que l'utilisateur actuel est actif.
    
    Args:
        current_user: L'utilisateur actuel
        
    Returns:
        L'utilisateur s'il est actif
        
    Raises:
        HTTPException: Si l'utilisateur est inactif
    """
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Utilisateur inactif")
    return current_user

async def get_current_active_superuser(
    current_user: models.User = Depends(get_current_user),
) -> models.User:
    """
    Vérifie que l'utilisateur actuel est un superutilisateur.
    
    Args:
        current_user: L'utilisateur actuel
        
    Returns:
        L'utilisateur s'il est superutilisateur
        
    Raises:
        HTTPException: Si l'utilisateur n'est pas superutilisateur
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=400, 
            detail="L'utilisateur n'a pas les privilèges suffisants"
        )
    return current_user
