"""
Router de ciclos
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Asignacion, Ciclo, Requerimiento, Usuario
from app.routers.auth import get_current_user
from app.schemas.asignacion import (AsignacionListResponse, AsignacionResponse,
                                    RequerimientoListResponse,
                                    RequerimientoResponse)

router = APIRouter()


@router.get("/{ciclo_id}")
async def get_ciclo(
    ciclo_id: int,
    current_user: Annotated[Usuario, Depends(get_current_user)],
    db: Session = Depends(get_db),
):
    """
    Obtiene un ciclo por ID.
    """
    ciclo = db.query(Ciclo).filter(Ciclo.id == ciclo_id).first()

    if not ciclo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Ciclo no encontrado"
        )

    return {
        "id": ciclo.id,
        "contrato_id": ciclo.contrato_id,
        "letra": ciclo.letra,
        "fecha_inicio": ciclo.fecha_inicio.isoformat(),
        "fecha_fin": ciclo.fecha_fin.isoformat(),
        "estado": ciclo.estado.value if ciclo.estado else "NO_DEFINIDO",
        "horario": ciclo.horario,
    }


@router.get("/{ciclo_id}/requerimientos", response_model=RequerimientoListResponse)
async def get_ciclo_requerimientos(
    ciclo_id: int,
    current_user: Annotated[Usuario, Depends(get_current_user)],
    db: Session = Depends(get_db),
):
    """
    Lista los requerimientos de un ciclo.
    """
    ciclo = db.query(Ciclo).filter(Ciclo.id == ciclo_id).first()
    if not ciclo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Ciclo no encontrado"
        )

    requerimientos = (
        db.query(Requerimiento).filter(Requerimiento.ciclo_id == ciclo_id).all()
    )

    result = []
    for r in requerimientos:
        # Contar asignados para este cargo en este ciclo
        cantidad_asignada = (
            db.query(func.count(Asignacion.id))
            .join(Asignacion.trabajador)
            .filter(
                Asignacion.ciclo_id == ciclo_id,
                Asignacion.trabajador.has(cargo_id=r.cargo_id),
            )
            .scalar()
        )

        result.append(
            RequerimientoResponse(
                id=r.id,
                ciclo_id=r.ciclo_id,
                cargo_id=r.cargo_id,
                cargo_nombre=r.cargo.nombre if r.cargo else None,
                cantidad_necesaria=r.cantidad_necesaria,
                cantidad_asignada=cantidad_asignada,
                completo=cantidad_asignada >= r.cantidad_necesaria,
                created_at=r.created_at,
                updated_at=r.updated_at,
            )
        )

    return RequerimientoListResponse(data=result)


@router.get("/{ciclo_id}/asignaciones", response_model=AsignacionListResponse)
async def get_ciclo_asignaciones(
    ciclo_id: int,
    current_user: Annotated[Usuario, Depends(get_current_user)],
    db: Session = Depends(get_db),
):
    """
    Lista las asignaciones de un ciclo.
    """
    ciclo = db.query(Ciclo).filter(Ciclo.id == ciclo_id).first()
    if not ciclo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Ciclo no encontrado"
        )

    asignaciones = db.query(Asignacion).filter(Asignacion.ciclo_id == ciclo_id).all()

    result = []
    for a in asignaciones:
        trabajador_nombre = None
        cargo_nombre = None

        if a.trabajador:
            trabajador_nombre = f"{a.trabajador.nombres} {a.trabajador.apellidos}"
            if a.trabajador.cargo:
                cargo_nombre = a.trabajador.cargo.nombre

        result.append(
            AsignacionResponse(
                id=a.id,
                ciclo_id=a.ciclo_id,
                trabajador_id=a.trabajador_id,
                trabajador_nombre=trabajador_nombre,
                cargo_nombre=cargo_nombre,
                fecha_asignacion=a.fecha_asignacion,
                created_at=a.created_at,
            )
        )

    return AsignacionListResponse(data=result)
