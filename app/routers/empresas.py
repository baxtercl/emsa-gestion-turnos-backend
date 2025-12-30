"""
Router de empresas
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Empresa, Usuario
from app.models.usuario import RolUsuario
from app.routers.auth import get_current_user
from app.schemas.empresa import (EmpresaCreate, EmpresaListResponse,
                                 EmpresaResponse, EmpresaUpdate)

router = APIRouter()


def require_admin(current_user: Usuario) -> None:
    """Verifica que el usuario sea ADMIN"""
    if current_user.rol != RolUsuario.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requieren permisos de administrador",
        )


@router.get("", response_model=EmpresaListResponse)
async def get_empresas(
    current_user: Annotated[Usuario, Depends(get_current_user)],
    db: Session = Depends(get_db),
    activo: bool = None,
):
    """
    Lista todas las empresas.
    Opcionalmente filtrar por estado activo.
    """
    query = db.query(Empresa)

    if activo is not None:
        query = query.filter(Empresa.activo == activo)

    empresas = query.order_by(Empresa.nombre).all()

    return EmpresaListResponse(
        data=[
            EmpresaResponse(
                id=e.id,
                nombre=e.nombre,
                rut=e.rut,
                es_mandante=e.es_mandante,
                activo=e.activo,
                created_at=e.created_at,
                updated_at=e.updated_at,
            )
            for e in empresas
        ]
    )


@router.get("/{empresa_id}", response_model=EmpresaResponse)
async def get_empresa(
    empresa_id: int,
    current_user: Annotated[Usuario, Depends(get_current_user)],
    db: Session = Depends(get_db),
):
    """
    Obtiene una empresa por ID.
    """
    empresa = db.query(Empresa).filter(Empresa.id == empresa_id).first()

    if not empresa:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Empresa no encontrada"
        )

    return EmpresaResponse(
        id=empresa.id,
        nombre=empresa.nombre,
        rut=empresa.rut,
        es_mandante=empresa.es_mandante,
        activo=empresa.activo,
        created_at=empresa.created_at,
        updated_at=empresa.updated_at,
    )


@router.post("", response_model=EmpresaResponse, status_code=status.HTTP_201_CREATED)
async def create_empresa(
    empresa_data: EmpresaCreate,
    current_user: Annotated[Usuario, Depends(get_current_user)],
    db: Session = Depends(get_db),
):
    """
    Crea una nueva empresa.
    Solo usuarios ADMIN pueden crear empresas.
    """
    require_admin(current_user)

    # Verificar que el RUT no exista
    if db.query(Empresa).filter(Empresa.rut == empresa_data.rut).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe una empresa con este RUT",
        )

    # Crear empresa
    nueva_empresa = Empresa(
        nombre=empresa_data.nombre,
        rut=empresa_data.rut,
        es_mandante=empresa_data.es_mandante,
        activo=True,
    )

    db.add(nueva_empresa)
    db.commit()
    db.refresh(nueva_empresa)

    return EmpresaResponse(
        id=nueva_empresa.id,
        nombre=nueva_empresa.nombre,
        rut=nueva_empresa.rut,
        es_mandante=nueva_empresa.es_mandante,
        activo=nueva_empresa.activo,
        created_at=nueva_empresa.created_at,
        updated_at=nueva_empresa.updated_at,
    )


@router.put("/{empresa_id}", response_model=EmpresaResponse)
async def update_empresa(
    empresa_id: int,
    empresa_data: EmpresaUpdate,
    current_user: Annotated[Usuario, Depends(get_current_user)],
    db: Session = Depends(get_db),
):
    """
    Actualiza una empresa existente.
    Solo usuarios ADMIN pueden actualizar empresas.
    """
    require_admin(current_user)

    empresa = db.query(Empresa).filter(Empresa.id == empresa_id).first()

    if not empresa:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Empresa no encontrada"
        )

    # Verificar unicidad de RUT si se está actualizando
    if empresa_data.rut and empresa_data.rut != empresa.rut:
        if db.query(Empresa).filter(Empresa.rut == empresa_data.rut).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya existe una empresa con este RUT",
            )

    # Actualizar campos proporcionados
    if empresa_data.nombre is not None:
        empresa.nombre = empresa_data.nombre
    if empresa_data.rut is not None:
        empresa.rut = empresa_data.rut
    if empresa_data.es_mandante is not None:
        empresa.es_mandante = empresa_data.es_mandante
    if empresa_data.activo is not None:
        empresa.activo = empresa_data.activo

    db.commit()
    db.refresh(empresa)

    return EmpresaResponse(
        id=empresa.id,
        nombre=empresa.nombre,
        rut=empresa.rut,
        es_mandante=empresa.es_mandante,
        activo=empresa.activo,
        created_at=empresa.created_at,
        updated_at=empresa.updated_at,
    )


@router.delete("/{empresa_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_empresa(
    empresa_id: int,
    current_user: Annotated[Usuario, Depends(get_current_user)],
    db: Session = Depends(get_db),
):
    """
    Elimina una empresa (soft delete).
    Solo usuarios ADMIN pueden eliminar empresas.
    """
    require_admin(current_user)

    empresa = db.query(Empresa).filter(Empresa.id == empresa_id).first()

    if not empresa:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Empresa no encontrada"
        )

    # Soft delete
    empresa.activo = False
    db.commit()

    return None
