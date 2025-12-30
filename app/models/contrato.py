"""
Modelo Contrato
"""

import enum

from sqlalchemy import (Boolean, Column, Date, DateTime, Enum, ForeignKey,
                        Integer, String)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class TipoTurnos(str, enum.Enum):
    """Tipos de turnos"""

    AB = "AB"
    ABCD = "ABCD"


class Contrato(Base):
    """Contratos entre proyecto, servicio y empresa contratista"""

    __tablename__ = "contratos"

    id = Column(Integer, primary_key=True, index=True)
    proyecto_id = Column(Integer, ForeignKey("proyectos.id"), nullable=False)
    servicio_id = Column(Integer, ForeignKey("servicios.id"), nullable=False)
    empresa_id = Column(Integer, ForeignKey("empresas.id"), nullable=False)
    tipo_turnos = Column(Enum(TipoTurnos), nullable=False, default=TipoTurnos.ABCD)
    patron = Column(String(10), nullable=False, default="7x7")
    activo = Column(Boolean, default=True, index=True)
    fecha_inicio = Column(Date)
    fecha_fin = Column(Date)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relaciones
    proyecto = relationship("Proyecto", back_populates="contratos")
    servicio = relationship("Servicio", back_populates="contratos")
    empresa = relationship("Empresa", back_populates="contratos")
    ciclos = relationship("Ciclo", back_populates="contrato")
