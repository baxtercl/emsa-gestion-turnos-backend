"""
Schemas para Ciclo
"""

from datetime import date, datetime
from typing import Any, List, Optional

from pydantic import BaseModel


class CoberturaResponse(BaseModel):
    """Cobertura de un ciclo"""

    requeridos: int
    asignados: int
    porcentaje: float


class CicloResponse(BaseModel):
    """Response de un ciclo"""

    id: int
    contrato_id: int
    letra: str  # A, B, C, D
    fecha_inicio: date
    fecha_fin: date
    estado: str  # NO_DEFINIDO, INCOMPLETO, COMPLETO
    horario: str = "DIA"
    cobertura: Optional[CoberturaResponse] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class CicloListResponse(BaseModel):
    """Response con lista de ciclos"""

    data: List[CicloResponse]


class CicloCalendarioEvento(BaseModel):
    """Evento de calendario para FullCalendar"""

    id: str
    title: str
    start: str  # ISO date
    end: str  # ISO date
    color: str  # Hex color
    extendedProps: dict


class CicloCalendarioResponse(BaseModel):
    """Response con eventos de calendario"""

    data: List[CicloCalendarioEvento]
