"""
Modelo Ciclo
"""

import enum

from sqlalchemy import (Column, Date, DateTime, Enum, ForeignKey, Integer,
                        String)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class EstadoCiclo(str, enum.Enum):
    """Estados de ciclo"""

    NO_DEFINIDO = "NO_DEFINIDO"
    INCOMPLETO = "INCOMPLETO"
    COMPLETO = "COMPLETO"


class Ciclo(Base):
    """Ciclos de turno (A, B, C, D) para cada contrato"""

    __tablename__ = "ciclos"

    id = Column(Integer, primary_key=True, index=True)
    contrato_id = Column(Integer, ForeignKey("contratos.id"), nullable=False)
    letra = Column(String(1), nullable=False)  # A, B, C, D
    fecha_inicio = Column(Date, nullable=False)
    fecha_fin = Column(Date, nullable=False)
    estado = Column(Enum(EstadoCiclo), default=EstadoCiclo.NO_DEFINIDO, index=True)
    horario = Column(String(10), default="DIA")  # DIA o NOCHE
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relaciones
    contrato = relationship("Contrato", back_populates="ciclos")
    asignaciones = relationship("Asignacion", back_populates="ciclo")
    requerimientos = relationship("Requerimiento", back_populates="ciclo")
