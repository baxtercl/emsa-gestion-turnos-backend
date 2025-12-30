"""
Router de autenticacion
"""

from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Usuario
from app.schemas.auth import LoginRequest, Token, UserResponse
from app.utils.security import (create_access_token, create_refresh_token,
                                decode_token, verify_password)

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)], db: Session = Depends(get_db)
) -> Usuario:
    """Obtiene el usuario actual desde el token JWT"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciales inválidas",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = decode_token(token)
    if payload is None:
        raise credentials_exception

    user_id_str = payload.get("sub")
    if user_id_str is None:
        raise credentials_exception

    # Convertir sub de string a int para la query
    try:
        user_id = int(user_id_str)
    except (ValueError, TypeError):
        raise credentials_exception

    user = db.query(Usuario).filter(Usuario.id == user_id).first()
    if user is None:
        raise credentials_exception

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuario inactivo"
        )

    return user


@router.post("/login", response_model=Token)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(get_db),
):
    """
    Login con email y password.
    Retorna access_token y refresh_token.
    """
    # Buscar usuario por email (username del form es el email)
    user = db.query(Usuario).filter(Usuario.email == form_data.username).first()

    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuario inactivo"
        )

    # Actualizar last_login
    user.last_login = datetime.utcnow()
    db.commit()

    # Crear tokens (sub debe ser string según estándar JWT)
    access_token = create_access_token(data={"sub": str(user.id), "email": user.email})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})

    return Token(
        access_token=access_token, refresh_token=refresh_token, token_type="bearer"
    )


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: Annotated[Usuario, Depends(get_current_user)]):
    """
    Retorna informacion del usuario autenticado.
    """
    return UserResponse(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        nombre_completo=current_user.nombre_completo,
        rol=current_user.rol.value,
        empresa_id=current_user.empresa_id,
        empresa_nombre=current_user.empresa.nombre if current_user.empresa else None,
        cargo=current_user.cargo,
        is_active=current_user.is_active,
    )


@router.post("/logout")
async def logout(current_user: Annotated[Usuario, Depends(get_current_user)]):
    """
    Logout del usuario.
    En una implementacion real, aqui se invalidaria el token.
    """
    return {"message": "Sesión cerrada exitosamente"}
