"""
Modelo Cargo
"""

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class Cargo(Base):
    """Cargos jerarquicos dentro de cada proyecto/empresa"""

    __tablename__ = "cargos"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(200), nullable=False)
    proyecto_id = Column(Integer, ForeignKey("proyectos.id"))
    empresa_id = Column(Integer, ForeignKey("empresas.id"))
    jefe_directo_id = Column(Integer, ForeignKey("cargos.id"))
    nivel = Column(
        String(20), default="OPERATIVO"
    )  # GERENCIA, JEFATURA, SUPERVISION, OPERATIVO
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relaciones
    proyecto = relationship("Proyecto", back_populates="cargos")
    empresa = relationship("Empresa", back_populates="cargos")
    jefe_directo = relationship("Cargo", remote_side=[id])
    trabajadores = relationship("Trabajador", back_populates="cargo")
    requerimientos = relationship("Requerimiento", back_populates="cargo")
