"""
Schemas para Asignacion y Requerimiento
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class AsignacionResponse(BaseModel):
    """Response de una asignacion"""

    id: int
    ciclo_id: int
    trabajador_id: int
    trabajador_nombre: Optional[str] = None
    cargo_nombre: Optional[str] = None
    fecha_asignacion: Optional[datetime] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class AsignacionListResponse(BaseModel):
    """Response con lista de asignaciones"""

    data: List[AsignacionResponse]


class RequerimientoResponse(BaseModel):
    """Response de un requerimiento"""

    id: int
    ciclo_id: int
    cargo_id: int
    cargo_nombre: Optional[str] = None
    cantidad_necesaria: int
    cantidad_asignada: Optional[int] = None
    completo: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class RequerimientoListResponse(BaseModel):
    """Response con lista de requerimientos"""

    data: List[RequerimientoResponse]
