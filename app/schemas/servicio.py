"""
Schemas para Servicio
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class ServicioCreate(BaseModel):
    """Request para crear servicio"""

    nombre: str
    descripcion: Optional[str] = None


class ServicioUpdate(BaseModel):
    """Request para actualizar servicio"""

    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    activo: Optional[bool] = None


class ServicioResponse(BaseModel):
    """Response de un servicio"""

    id: int
    nombre: str
    descripcion: Optional[str] = None
    activo: bool = True
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ServicioListResponse(BaseModel):
    """Response con lista de servicios"""

    data: List[ServicioResponse]
