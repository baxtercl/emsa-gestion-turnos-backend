"""
Router de usuarios
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Empresa, Usuario
from app.models.usuario import RolUsuario
from app.routers.auth import get_current_user
from app.schemas.usuario import (UsuarioCreate, UsuarioListResponse,
                                 UsuarioResponse, UsuarioUpdate)
from app.utils.security import get_password_hash

router = APIRouter()


def require_admin(current_user: Usuario) -> None:
    """Verifica que el usuario sea ADMIN"""
    if current_user.rol != RolUsuario.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requieren permisos de administrador",
        )


@router.get("", response_model=UsuarioListResponse)
async def get_usuarios(
    current_user: Annotated[Usuario, Depends(get_current_user)],
    db: Session = Depends(get_db),
    activo: bool = None,
):
    """
    Lista todos los usuarios.
    Opcionalmente filtrar por estado activo.
    """
    query = db.query(Usuario)

    if activo is not None:
        query = query.filter(Usuario.is_active == activo)

    usuarios = query.order_by(Usuario.nombre_completo).all()

    return UsuarioListResponse(
        data=[
            UsuarioResponse(
                id=u.id,
                username=u.username,
                email=u.email,
                nombre_completo=u.nombre_completo,
                rol=u.rol.value,
                empresa_id=u.empresa_id,
                empresa_nombre=u.empresa.nombre if u.empresa else None,
                cargo=u.cargo,
                is_active=u.is_active,
                last_login=u.last_login,
                created_at=u.created_at,
                updated_at=u.updated_at,
            )
            for u in usuarios
        ]
    )


@router.get("/{usuario_id}", response_model=UsuarioResponse)
async def get_usuario(
    usuario_id: int,
    current_user: Annotated[Usuario, Depends(get_current_user)],
    db: Session = Depends(get_db),
):
    """
    Obtiene un usuario por ID.
    """
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()

    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado"
        )

    return UsuarioResponse(
        id=usuario.id,
        username=usuario.username,
        email=usuario.email,
        nombre_completo=usuario.nombre_completo,
        rol=usuario.rol.value,
        empresa_id=usuario.empresa_id,
        empresa_nombre=usuario.empresa.nombre if usuario.empresa else None,
        cargo=usuario.cargo,
        is_active=usuario.is_active,
        last_login=usuario.last_login,
        created_at=usuario.created_at,
        updated_at=usuario.updated_at,
    )


@router.post("", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED)
async def create_usuario(
    usuario_data: UsuarioCreate,
    current_user: Annotated[Usuario, Depends(get_current_user)],
    db: Session = Depends(get_db),
):
    """
    Crea un nuevo usuario.
    Solo usuarios ADMIN pueden crear usuarios.
    """
    require_admin(current_user)

    # Verificar que el email no exista
    if db.query(Usuario).filter(Usuario.email == usuario_data.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe un usuario con este email",
        )

    # Verificar que el username no exista
    if db.query(Usuario).filter(Usuario.username == usuario_data.username).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe un usuario con este nombre de usuario",
        )

    # Verificar que la empresa exista si se proporciona
    if usuario_data.empresa_id:
        empresa = (
            db.query(Empresa).filter(Empresa.id == usuario_data.empresa_id).first()
        )
        if not empresa:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La empresa especificada no existe",
            )

    # Crear usuario
    nuevo_usuario = Usuario(
        username=usuario_data.username,
        email=usuario_data.email,
        password_hash=get_password_hash(usuario_data.password),
        nombre_completo=usuario_data.nombre_completo,
        rol=usuario_data.rol,
        empresa_id=usuario_data.empresa_id,
        cargo=usuario_data.cargo,
        is_active=True,
    )

    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)

    return UsuarioResponse(
        id=nuevo_usuario.id,
        username=nuevo_usuario.username,
        email=nuevo_usuario.email,
        nombre_completo=nuevo_usuario.nombre_completo,
        rol=nuevo_usuario.rol.value,
        empresa_id=nuevo_usuario.empresa_id,
        empresa_nombre=nuevo_usuario.empresa.nombre if nuevo_usuario.empresa else None,
        cargo=nuevo_usuario.cargo,
        is_active=nuevo_usuario.is_active,
        last_login=nuevo_usuario.last_login,
        created_at=nuevo_usuario.created_at,
        updated_at=nuevo_usuario.updated_at,
    )


@router.put("/{usuario_id}", response_model=UsuarioResponse)
async def update_usuario(
    usuario_id: int,
    usuario_data: UsuarioUpdate,
    current_user: Annotated[Usuario, Depends(get_current_user)],
    db: Session = Depends(get_db),
):
    """
    Actualiza un usuario existente.
    Solo usuarios ADMIN pueden actualizar usuarios.
    """
    require_admin(current_user)

    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()

    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado"
        )

    # Verificar unicidad de email si se está actualizando
    if usuario_data.email and usuario_data.email != usuario.email:
        if db.query(Usuario).filter(Usuario.email == usuario_data.email).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya existe un usuario con este email",
            )

    # Verificar unicidad de username si se está actualizando
    if usuario_data.username and usuario_data.username != usuario.username:
        if db.query(Usuario).filter(Usuario.username == usuario_data.username).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya existe un usuario con este nombre de usuario",
            )

    # Verificar que la empresa exista si se proporciona
    if usuario_data.empresa_id:
        empresa = (
            db.query(Empresa).filter(Empresa.id == usuario_data.empresa_id).first()
        )
        if not empresa:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La empresa especificada no existe",
            )

    # Actualizar campos proporcionados
    if usuario_data.username is not None:
        usuario.username = usuario_data.username
    if usuario_data.email is not None:
        usuario.email = usuario_data.email
    if usuario_data.nombre_completo is not None:
        usuario.nombre_completo = usuario_data.nombre_completo
    if usuario_data.rol is not None:
        usuario.rol = usuario_data.rol
    if usuario_data.empresa_id is not None:
        usuario.empresa_id = usuario_data.empresa_id
    if usuario_data.cargo is not None:
        usuario.cargo = usuario_data.cargo
    if usuario_data.is_active is not None:
        usuario.is_active = usuario_data.is_active
    if usuario_data.password:
        usuario.password_hash = get_password_hash(usuario_data.password)

    db.commit()
    db.refresh(usuario)

    return UsuarioResponse(
        id=usuario.id,
        username=usuario.username,
        email=usuario.email,
        nombre_completo=usuario.nombre_completo,
        rol=usuario.rol.value,
        empresa_id=usuario.empresa_id,
        empresa_nombre=usuario.empresa.nombre if usuario.empresa else None,
        cargo=usuario.cargo,
        is_active=usuario.is_active,
        last_login=usuario.last_login,
        created_at=usuario.created_at,
        updated_at=usuario.updated_at,
    )


@router.delete("/{usuario_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_usuario(
    usuario_id: int,
    current_user: Annotated[Usuario, Depends(get_current_user)],
    db: Session = Depends(get_db),
):
    """
    Elimina un usuario (soft delete).
    Solo usuarios ADMIN pueden eliminar usuarios.
    """
    require_admin(current_user)

    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()

    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado"
        )

    # No permitir eliminarse a sí mismo
    if usuario.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No puedes eliminar tu propio usuario",
        )

    # Soft delete
    usuario.is_active = False
    db.commit()

    return None
