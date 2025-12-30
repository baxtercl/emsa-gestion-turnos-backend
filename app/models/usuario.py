"""
Modelo Usuario
"""

import enum

from sqlalchemy import (Boolean, Column, DateTime, Enum, ForeignKey, Integer,
                        String, Table)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class RolUsuario(str, enum.Enum):
    """Roles de usuario del sistema"""

    ADMIN = "ADMIN"
    GESTOR_PROYECTOS = "GESTOR_PROYECTOS"
    JEFE_PROYECTO = "JEFE_PROYECTO"
    CONTRATISTA = "CONTRATISTA"


# Tabla de relacion N:M entre usuarios y proyectos
usuarios_proyectos = Table(
    "usuarios_proyectos",
    Base.metadata,
    Column("usuario_id", Integer, ForeignKey("usuarios.id"), primary_key=True),
    Column("proyecto_id", Integer, ForeignKey("proyectos.id"), primary_key=True),
    Column("fecha_asignacion", DateTime(timezone=True), server_default=func.now()),
)


class Usuario(Base):
    """Usuarios del sistema con diferentes roles"""

    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(200), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    nombre_completo = Column(String(200))
    rol = Column(Enum(RolUsuario), nullable=False, default=RolUsuario.CONTRATISTA)
    empresa_id = Column(Integer, ForeignKey("empresas.id"))
    cargo = Column(String(100))
    is_active = Column(Boolean, default=True)
    last_login = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relaciones
    empresa = relationship("Empresa", back_populates="usuarios")
    proyectos_asignados = relationship(
        "Proyecto", secondary=usuarios_proyectos, back_populates="jefes_asignados"
    )
