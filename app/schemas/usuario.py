"""
Schemas para Usuario
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr

from app.models.usuario import RolUsuario


class UsuarioCreate(BaseModel):
    """Request para crear usuario"""

    username: str
    email: EmailStr
    nombre_completo: str
    rol: RolUsuario
    empresa_id: Optional[int] = None
    cargo: Optional[str] = None
    password: str


class UsuarioUpdate(BaseModel):
    """Request para actualizar usuario"""

    username: Optional[str] = None
    email: Optional[EmailStr] = None
    nombre_completo: Optional[str] = None
    rol: Optional[RolUsuario] = None
    empresa_id: Optional[int] = None
    cargo: Optional[str] = None
    is_active: Optional[bool] = None
    password: Optional[str] = None


class UsuarioResponse(BaseModel):
    """Response de un usuario"""

    id: int
    username: str
    email: str
    nombre_completo: Optional[str] = None
    rol: str
    empresa_id: Optional[int] = None
    empresa_nombre: Optional[str] = None
    cargo: Optional[str] = None
    is_active: bool
    last_login: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class UsuarioListResponse(BaseModel):
    """Response con lista de usuarios"""

    data: list[UsuarioResponse]
