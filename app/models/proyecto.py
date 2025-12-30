"""
Modelo Proyecto
"""

from sqlalchemy import Boolean, Column, Date, DateTime, Integer, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base
from app.models.usuario import usuarios_proyectos


class Proyecto(Base):
    """Proyectos mineros gestionados por EMSA"""

    __tablename__ = "proyectos"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(200), nullable=False)
    descripcion = Column(Text)
    activo = Column(Boolean, default=True, index=True)
    fecha_inicio = Column(Date, nullable=False)
    fecha_fin = Column(Date)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relaciones
    contratos = relationship("Contrato", back_populates="proyecto")
    trabajadores = relationship("Trabajador", back_populates="proyecto")
    cargos = relationship("Cargo", back_populates="proyecto")
    jefes_asignados = relationship(
        "Usuario", secondary=usuarios_proyectos, back_populates="proyectos_asignados"
    )
