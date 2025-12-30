"""
Modelo Trabajador
"""

from sqlalchemy import (Boolean, Column, Date, DateTime, ForeignKey, Integer,
                        String)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class Trabajador(Base):
    """Trabajadores de las empresas contratistas"""

    __tablename__ = "trabajadores"

    id = Column(Integer, primary_key=True, index=True)
    rut = Column(String(12), unique=True, nullable=False, index=True)
    nombres = Column(String(200), nullable=False)
    apellidos = Column(String(200), nullable=False)
    email = Column(String(200))
    telefono = Column(String(20))
    proyecto_id = Column(Integer, ForeignKey("proyectos.id"))
    empresa_id = Column(Integer, ForeignKey("empresas.id"), nullable=False)
    cargo_id = Column(Integer, ForeignKey("cargos.id"))
    activo = Column(Boolean, default=True, index=True)
    fecha_ingreso = Column(Date)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relaciones
    proyecto = relationship("Proyecto", back_populates="trabajadores")
    empresa = relationship("Empresa", back_populates="trabajadores")
    cargo = relationship("Cargo", back_populates="trabajadores")
    asignaciones = relationship("Asignacion", back_populates="trabajador")

    @property
    def nombre_completo(self) -> str:
        """Retorna nombre completo del trabajador"""
        return f"{self.nombres} {self.apellidos}"
