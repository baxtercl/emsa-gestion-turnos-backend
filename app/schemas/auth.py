"""
Schemas para autenticacion
"""

from typing import Optional

from pydantic import BaseModel, EmailStr


class LoginRequest(BaseModel):
    """Request para login"""

    email: EmailStr
    password: str


class Token(BaseModel):
    """Response con tokens de acceso"""

    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Datos codificados en el token"""

    user_id: Optional[int] = None
    email: Optional[str] = None


class UserResponse(BaseModel):
    """Response con datos del usuario"""

    id: int
    username: str
    email: str
    nombre_completo: Optional[str] = None
    rol: str
    empresa_id: Optional[int] = None
    empresa_nombre: Optional[str] = None
    cargo: Optional[str] = None
    is_active: bool

    class Config:
        from_attributes = True
