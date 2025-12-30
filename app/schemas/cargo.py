"""
Schemas para Cargo
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class CargoResponse(BaseModel):
    """Response de un cargo"""

    id: int
    nombre: str
    proyecto_id: Optional[int] = None
    empresa_id: Optional[int] = None
    empresa_nombre: Optional[str] = None
    jefe_directo_id: Optional[int] = None
    jefe_directo_nombre: Optional[str] = None
    nivel: str = "OPERATIVO"
    subordinados_count: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class CargoListResponse(BaseModel):
    """Response con lista de cargos"""

    data: List[CargoResponse]


class CargoTreeNode(BaseModel):
    """Nodo del arbol organizacional"""

    id: int
    nombre: str
    nivel: str
    empresa_nombre: Optional[str] = None
    children: List["CargoTreeNode"] = []

    class Config:
        from_attributes = True


# Necesario para referencias circulares
CargoTreeNode.model_rebuild()


class CargoTreeResponse(BaseModel):
    """Response con arbol organizacional"""

    data: CargoTreeNode
