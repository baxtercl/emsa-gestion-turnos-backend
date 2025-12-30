"""
Schemas Pydantic para validacion de request/response
"""

from app.schemas.asignacion import (AsignacionListResponse, AsignacionResponse,
                                    RequerimientoListResponse,
                                    RequerimientoResponse)
from app.schemas.auth import LoginRequest, Token, TokenData, UserResponse
from app.schemas.cargo import CargoListResponse, CargoResponse, CargoTreeNode
from app.schemas.ciclo import (CicloCalendarioEvento, CicloCalendarioResponse,
                               CicloListResponse, CicloResponse,
                               CoberturaResponse)
from app.schemas.contrato import ContratoListResponse, ContratoResponse
from app.schemas.empresa import EmpresaListResponse, EmpresaResponse
from app.schemas.proyecto import (PanelMandanteResponse, ProyectoListResponse,
                                  ProyectoResponse)
from app.schemas.servicio import ServicioListResponse, ServicioResponse
from app.schemas.trabajador import TrabajadorListResponse, TrabajadorResponse

__all__ = [
    # Auth
    "Token",
    "TokenData",
    "LoginRequest",
    "UserResponse",
    # Empresa
    "EmpresaResponse",
    "EmpresaListResponse",
    # Servicio
    "ServicioResponse",
    "ServicioListResponse",
    # Proyecto
    "ProyectoResponse",
    "ProyectoListResponse",
    "PanelMandanteResponse",
    # Contrato
    "ContratoResponse",
    "ContratoListResponse",
    # Cargo
    "CargoResponse",
    "CargoListResponse",
    "CargoTreeNode",
    # Trabajador
    "TrabajadorResponse",
    "TrabajadorListResponse",
    # Ciclo
    "CicloResponse",
    "CicloListResponse",
    "CicloCalendarioEvento",
    "CicloCalendarioResponse",
    "CoberturaResponse",
    # Asignacion
    "AsignacionResponse",
    "AsignacionListResponse",
    "RequerimientoResponse",
    "RequerimientoListResponse",
]
