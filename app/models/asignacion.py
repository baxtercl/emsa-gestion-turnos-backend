"""
Modelos Asignacion y Requerimiento
"""

from sqlalchemy import Column, DateTime, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class Requerimiento(Base):
    """Cantidad de trabajadores requeridos por cargo en cada ciclo"""

    __tablename__ = "requerimientos"

    id = Column(Integer, primary_key=True, index=True)
    ciclo_id = Column(Integer, ForeignKey("ciclos.id"), nullable=False)
    cargo_id = Column(Integer, ForeignKey("cargos.id"), nullable=False)
    cantidad_necesaria = Column(Integer, nullable=False, default=1)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Constraint unico
    __table_args__ = (
        UniqueConstraint("ciclo_id", "cargo_id", name="unique_requerimiento"),
    )

    # Relaciones
    ciclo = relationship("Ciclo", back_populates="requerimientos")
    cargo = relationship("Cargo", back_populates="requerimientos")


class Asignacion(Base):
    """Asignacion de trabajadores a ciclos de turno"""

    __tablename__ = "asignaciones"

    id = Column(Integer, primary_key=True, index=True)
    ciclo_id = Column(Integer, ForeignKey("ciclos.id"), nullable=False, index=True)
    trabajador_id = Column(
        Integer, ForeignKey("trabajadores.id"), nullable=False, index=True
    )
    fecha_asignacion = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Constraint unico
    __table_args__ = (
        UniqueConstraint("ciclo_id", "trabajador_id", name="unique_asignacion"),
    )

    # Relaciones
    ciclo = relationship("Ciclo", back_populates="asignaciones")
    trabajador = relationship("Trabajador", back_populates="asignaciones")
