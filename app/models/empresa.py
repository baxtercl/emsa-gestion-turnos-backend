"""
Modelo Empresa
"""

from sqlalchemy import Boolean, Column, DateTime, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class Empresa(Base):
    """Empresas del sistema: mandante (EMSA) y contratistas"""

    __tablename__ = "empresas"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(200), nullable=False)
    rut = Column(String(12), unique=True, nullable=False)
    es_mandante = Column(Boolean, default=False)
    activo = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relaciones
    usuarios = relationship("Usuario", back_populates="empresa")
    contratos = relationship("Contrato", back_populates="empresa")
    trabajadores = relationship("Trabajador", back_populates="empresa")
    cargos = relationship("Cargo", back_populates="empresa")
