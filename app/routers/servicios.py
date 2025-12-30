"""
Router de servicios
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Servicio, Usuario
from app.models.usuario import RolUsuario
from app.routers.auth import get_current_user
from app.schemas.servicio import (ServicioCreate, ServicioListResponse,
                                  ServicioResponse, ServicioUpdate)

router = APIRouter()


def require_admin(current_user: Usuario) -> None:
    """Verifica que el usuario sea ADMIN"""
    if current_user.rol != RolUsuario.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requieren permisos de administrador",
        )


@router.get("", response_model=ServicioListResponse)
async def get_servicios(
    current_user: Annotated[Usuario, Depends(get_current_user)],
    db: Session = Depends(get_db),
    activo: bool = None,
):
    """
    Lista todos los servicios.
    Opcionalmente filtrar por estado activo.
    """
    query = db.query(Servicio)

    if activo is not None:
        query = query.filter(Servicio.activo == activo)

    servicios = query.order_by(Servicio.nombre).all()

    return ServicioListResponse(
        data=[
            ServicioResponse(
                id=s.id,
                nombre=s.nombre,
                descripcion=s.descripcion,
                activo=s.activo,
                created_at=s.created_at,
            )
            for s in servicios
        ]
    )


@router.get("/{servicio_id}", response_model=ServicioResponse)
async def get_servicio(
    servicio_id: int,
    current_user: Annotated[Usuario, Depends(get_current_user)],
    db: Session = Depends(get_db),
):
    """
    Obtiene un servicio por ID.
    """
    servicio = db.query(Servicio).filter(Servicio.id == servicio_id).first()

    if not servicio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Servicio no encontrado"
        )

    return ServicioResponse(
        id=servicio.id,
        nombre=servicio.nombre,
        descripcion=servicio.descripcion,
        activo=servicio.activo,
        created_at=servicio.created_at,
    )


@router.post("", response_model=ServicioResponse, status_code=status.HTTP_201_CREATED)
async def create_servicio(
    servicio_data: ServicioCreate,
    current_user: Annotated[Usuario, Depends(get_current_user)],
    db: Session = Depends(get_db),
):
    """
    Crea un nuevo servicio.
    Solo usuarios ADMIN pueden crear servicios.
    """
    require_admin(current_user)

    # Verificar que el nombre no exista
    if db.query(Servicio).filter(Servicio.nombre == servicio_data.nombre).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe un servicio con este nombre",
        )

    # Crear servicio
    nuevo_servicio = Servicio(
        nombre=servicio_data.nombre,
        descripcion=servicio_data.descripcion,
        activo=True,
    )

    db.add(nuevo_servicio)
    db.commit()
    db.refresh(nuevo_servicio)

    return ServicioResponse(
        id=nuevo_servicio.id,
        nombre=nuevo_servicio.nombre,
        descripcion=nuevo_servicio.descripcion,
        activo=nuevo_servicio.activo,
        created_at=nuevo_servicio.created_at,
    )


@router.put("/{servicio_id}", response_model=ServicioResponse)
async def update_servicio(
    servicio_id: int,
    servicio_data: ServicioUpdate,
    current_user: Annotated[Usuario, Depends(get_current_user)],
    db: Session = Depends(get_db),
):
    """
    Actualiza un servicio existente.
    Solo usuarios ADMIN pueden actualizar servicios.
    """
    require_admin(current_user)

    servicio = db.query(Servicio).filter(Servicio.id == servicio_id).first()

    if not servicio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Servicio no encontrado"
        )

    # Verificar unicidad de nombre si se está actualizando
    if servicio_data.nombre and servicio_data.nombre != servicio.nombre:
        if db.query(Servicio).filter(Servicio.nombre == servicio_data.nombre).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya existe un servicio con este nombre",
            )

    # Actualizar campos proporcionados
    if servicio_data.nombre is not None:
        servicio.nombre = servicio_data.nombre
    if servicio_data.descripcion is not None:
        servicio.descripcion = servicio_data.descripcion
    if servicio_data.activo is not None:
        servicio.activo = servicio_data.activo

    db.commit()
    db.refresh(servicio)

    return ServicioResponse(
        id=servicio.id,
        nombre=servicio.nombre,
        descripcion=servicio.descripcion,
        activo=servicio.activo,
        created_at=servicio.created_at,
    )


@router.delete("/{servicio_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_servicio(
    servicio_id: int,
    current_user: Annotated[Usuario, Depends(get_current_user)],
    db: Session = Depends(get_db),
):
    """
    Elimina un servicio (soft delete).
    Solo usuarios ADMIN pueden eliminar servicios.
    """
    require_admin(current_user)

    servicio = db.query(Servicio).filter(Servicio.id == servicio_id).first()

    if not servicio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Servicio no encontrado"
        )

    # Soft delete
    servicio.activo = False
    db.commit()

    return None
