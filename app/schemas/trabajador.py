"""
Schemas para Trabajador
"""

from datetime import date, datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr


class TrabajadorCreate(BaseModel):
    """Request para crear trabajador"""

    rut: str
    nombres: str
    apellidos: str
    email: Optional[EmailStr] = None
    telefono: Optional[str] = None
    empresa_id: int
    cargo_id: Optional[int] = None
    fecha_ingreso: Optional[date] = None


class TrabajadorUpdate(BaseModel):
    """Request para actualizar trabajador"""

    rut: Optional[str] = None
    nombres: Optional[str] = None
    apellidos: Optional[str] = None
    email: Optional[EmailStr] = None
    telefono: Optional[str] = None
    empresa_id: Optional[int] = None
    cargo_id: Optional[int] = None
    activo: Optional[bool] = None
    fecha_ingreso: Optional[date] = None


class TrabajadorResponse(BaseModel):
    """Response de un trabajador"""

    id: int
    rut: str
    nombres: str
    apellidos: str
    nombre_completo: Optional[str] = None
    email: Optional[str] = None
    telefono: Optional[str] = None
    proyecto_id: Optional[int] = None
    empresa_id: int
    empresa_nombre: Optional[str] = None
    cargo_id: Optional[int] = None
    cargo_nombre: Optional[str] = None
    activo: bool = True
    fecha_ingreso: Optional[date] = None
    asignaciones_activas: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class TrabajadorListResponse(BaseModel):
    """Response con lista de trabajadores"""

    data: List[TrabajadorResponse]
