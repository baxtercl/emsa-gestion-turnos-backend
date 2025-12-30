"""
Router de trabajadores
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Cargo, Empresa, Trabajador, Usuario
from app.models.usuario import RolUsuario
from app.routers.auth import get_current_user
from app.schemas.trabajador import TrabajadorResponse, TrabajadorUpdate

router = APIRouter()


def require_admin_or_gestor(current_user: Usuario) -> None:
    """Verifica que el usuario sea ADMIN o GESTOR_PROYECTOS"""
    if current_user.rol not in [RolUsuario.ADMIN, RolUsuario.GESTOR_PROYECTOS]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requieren permisos de administrador o gestor de proyectos",
        )


@router.get("/{trabajador_id}", response_model=TrabajadorResponse)
async def get_trabajador(
    trabajador_id: int,
    current_user: Annotated[Usuario, Depends(get_current_user)],
    db: Session = Depends(get_db),
):
    """
    Obtiene un trabajador por ID.
    """
    trabajador = db.query(Trabajador).filter(Trabajador.id == trabajador_id).first()

    if not trabajador:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Trabajador no encontrado"
        )

    return TrabajadorResponse(
        id=trabajador.id,
        rut=trabajador.rut,
        nombres=trabajador.nombres,
        apellidos=trabajador.apellidos,
        nombre_completo=f"{trabajador.nombres} {trabajador.apellidos}",
        email=trabajador.email,
        telefono=trabajador.telefono,
        proyecto_id=trabajador.proyecto_id,
        empresa_id=trabajador.empresa_id,
        empresa_nombre=trabajador.empresa.nombre if trabajador.empresa else None,
        cargo_id=trabajador.cargo_id,
        cargo_nombre=trabajador.cargo.nombre if trabajador.cargo else None,
        activo=trabajador.activo,
        fecha_ingreso=trabajador.fecha_ingreso,
        created_at=trabajador.created_at,
        updated_at=trabajador.updated_at,
    )


@router.put("/{trabajador_id}", response_model=TrabajadorResponse)
async def update_trabajador(
    trabajador_id: int,
    trabajador_data: TrabajadorUpdate,
    current_user: Annotated[Usuario, Depends(get_current_user)],
    db: Session = Depends(get_db),
):
    """
    Actualiza un trabajador existente.
    Solo usuarios ADMIN o GESTOR_PROYECTOS pueden actualizar trabajadores.
    """
    require_admin_or_gestor(current_user)

    trabajador = db.query(Trabajador).filter(Trabajador.id == trabajador_id).first()

    if not trabajador:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Trabajador no encontrado"
        )

    # Verificar unicidad de RUT si se está actualizando
    if trabajador_data.rut and trabajador_data.rut != trabajador.rut:
        if db.query(Trabajador).filter(Trabajador.rut == trabajador_data.rut).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya existe un trabajador con este RUT",
            )

    # Verificar que la empresa exista si se proporciona
    if trabajador_data.empresa_id:
        empresa = (
            db.query(Empresa).filter(Empresa.id == trabajador_data.empresa_id).first()
        )
        if not empresa:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La empresa especificada no existe",
            )

    # Verificar que el cargo exista si se proporciona
    if trabajador_data.cargo_id:
        cargo = db.query(Cargo).filter(Cargo.id == trabajador_data.cargo_id).first()
        if not cargo:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El cargo especificado no existe",
            )

    # Actualizar campos proporcionados
    if trabajador_data.rut is not None:
        trabajador.rut = trabajador_data.rut
    if trabajador_data.nombres is not None:
        trabajador.nombres = trabajador_data.nombres
    if trabajador_data.apellidos is not None:
        trabajador.apellidos = trabajador_data.apellidos
    if trabajador_data.email is not None:
        trabajador.email = trabajador_data.email
    if trabajador_data.telefono is not None:
        trabajador.telefono = trabajador_data.telefono
    if trabajador_data.empresa_id is not None:
        trabajador.empresa_id = trabajador_data.empresa_id
    if trabajador_data.cargo_id is not None:
        trabajador.cargo_id = trabajador_data.cargo_id
    if trabajador_data.activo is not None:
        trabajador.activo = trabajador_data.activo
    if trabajador_data.fecha_ingreso is not None:
        trabajador.fecha_ingreso = trabajador_data.fecha_ingreso

    db.commit()
    db.refresh(trabajador)

    return TrabajadorResponse(
        id=trabajador.id,
        rut=trabajador.rut,
        nombres=trabajador.nombres,
        apellidos=trabajador.apellidos,
        nombre_completo=f"{trabajador.nombres} {trabajador.apellidos}",
        email=trabajador.email,
        telefono=trabajador.telefono,
        proyecto_id=trabajador.proyecto_id,
        empresa_id=trabajador.empresa_id,
        empresa_nombre=trabajador.empresa.nombre if trabajador.empresa else None,
        cargo_id=trabajador.cargo_id,
        cargo_nombre=trabajador.cargo.nombre if trabajador.cargo else None,
        activo=trabajador.activo,
        fecha_ingreso=trabajador.fecha_ingreso,
        created_at=trabajador.created_at,
        updated_at=trabajador.updated_at,
    )


@router.delete("/{trabajador_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_trabajador(
    trabajador_id: int,
    current_user: Annotated[Usuario, Depends(get_current_user)],
    db: Session = Depends(get_db),
):
    """
    Elimina un trabajador (soft delete).
    Solo usuarios ADMIN o GESTOR_PROYECTOS pueden eliminar trabajadores.
    """
    require_admin_or_gestor(current_user)

    trabajador = db.query(Trabajador).filter(Trabajador.id == trabajador_id).first()

    if not trabajador:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Trabajador no encontrado"
        )

    # Soft delete
    trabajador.activo = False
    db.commit()

    return None
