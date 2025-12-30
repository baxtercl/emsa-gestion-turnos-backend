"""
Schemas para Proyecto
"""

from datetime import date, datetime
from typing import Any, List, Optional

from pydantic import BaseModel


class ProyectoResponse(BaseModel):
    """Response de un proyecto"""

    id: int
    nombre: str
    descripcion: Optional[str] = None
    activo: bool
    fecha_inicio: date
    fecha_fin: Optional[date] = None
    contratos_count: Optional[int] = None
    trabajadores_count: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ProyectoListResponse(BaseModel):
    """Response con lista de proyectos"""

    data: List[ProyectoResponse]


class ContratoResumenResponse(BaseModel):
    """Resumen de contrato para panel mandante"""

    contrato_id: int
    empresa: str
    servicio: str
    patron: str
    tipo_turnos: str
    ciclo_actual: Optional[Any] = None
    dotacion_requerida: int = 0
    dotacion_asignada: int = 0


class AlertaResponse(BaseModel):
    """Alerta para panel mandante"""

    tipo: str  # "warning" | "danger"
    mensaje: str
    contrato_id: int


class StatsResponse(BaseModel):
    """Estadisticas del proyecto"""

    total_trabajadores: int
    trabajadores_asignados: int
    total_contratos: int
    ciclo_actual: Optional[Any] = None


class PanelMandanteResponse(BaseModel):
    """Response del panel de mandante"""

    proyecto: dict
    resumen_contratos: List[ContratoResumenResponse]
    alertas: List[AlertaResponse]
    stats: StatsResponse
