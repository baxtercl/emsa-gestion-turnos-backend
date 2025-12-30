"""
Schemas para Contrato
"""

from datetime import date, datetime
from typing import List, Optional

from pydantic import BaseModel


class ContratoResponse(BaseModel):
    """Response de un contrato"""

    id: int
    proyecto_id: int
    servicio_id: int
    empresa_id: int
    tipo_turnos: str
    patron: str
    activo: bool = True
    fecha_inicio: Optional[date] = None
    fecha_fin: Optional[date] = None
    # Campos adicionales con join
    empresa_nombre: Optional[str] = None
    servicio_nombre: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ContratoListResponse(BaseModel):
    """Response con lista de contratos"""

    data: List[ContratoResponse]
