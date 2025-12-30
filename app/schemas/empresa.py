"""
Schemas para Empresa
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class EmpresaCreate(BaseModel):
    """Request para crear empresa"""

    nombre: str
    rut: str
    es_mandante: bool = False


class EmpresaUpdate(BaseModel):
    """Request para actualizar empresa"""

    nombre: Optional[str] = None
    rut: Optional[str] = None
    es_mandante: Optional[bool] = None
    activo: Optional[bool] = None


class EmpresaResponse(BaseModel):
    """Response de una empresa"""

    id: int
    nombre: str
    rut: str
    es_mandante: bool
    activo: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class EmpresaListResponse(BaseModel):
    """Response con lista de empresas"""

    data: List[EmpresaResponse]
