"""
Sistema de permisos RBAC (Role-Based Access Control)
"""

from enum import Enum
from typing import List

from fastapi import HTTPException, status

from app.models.usuario import RolUsuario


class Permission(str, Enum):
    """Permisos disponibles en el sistema"""

    # Proyectos
    PROYECTOS_VER_TODOS = "PROYECTOS_VER_TODOS"
    PROYECTOS_CREAR = "PROYECTOS_CREAR"
    PROYECTOS_EDITAR = "PROYECTOS_EDITAR"
    PROYECTOS_ELIMINAR = "PROYECTOS_ELIMINAR"

    # Contratos
    CONTRATOS_VER_TODOS = "CONTRATOS_VER_TODOS"
    CONTRATOS_CREAR = "CONTRATOS_CREAR"
    CONTRATOS_EDITAR = "CONTRATOS_EDITAR"
    CONTRATOS_ELIMINAR = "CONTRATOS_ELIMINAR"

    # Dotacion
    DOTACION_VER_TODOS = "DOTACION_VER_TODOS"
    DOTACION_GESTIONAR = "DOTACION_GESTIONAR"

    # Ciclos
    CICLOS_VER = "CICLOS_VER"
    CICLOS_CREAR = "CICLOS_CREAR"
    CICLOS_EDITAR = "CICLOS_EDITAR"
    CICLOS_ELIMINAR = "CICLOS_ELIMINAR"

    # Asignaciones
    ASIGNACIONES_VER = "ASIGNACIONES_VER"
    ASIGNACIONES_GESTIONAR = "ASIGNACIONES_GESTIONAR"

    # Administracion
    USUARIOS_GESTIONAR = "USUARIOS_GESTIONAR"
    EMPRESAS_GESTIONAR = "EMPRESAS_GESTIONAR"
    SERVICIOS_GESTIONAR = "SERVICIOS_GESTIONAR"
    CONFIGURACION = "CONFIGURACION"
    REPORTES_GLOBALES = "REPORTES_GLOBALES"


# Mapeo de permisos por rol
ROLE_PERMISSIONS: dict[RolUsuario, List[Permission]] = {
    RolUsuario.ADMIN: list(Permission),  # Todos los permisos
    RolUsuario.GESTOR_PROYECTOS: [
        Permission.PROYECTOS_VER_TODOS,
        Permission.PROYECTOS_CREAR,
        Permission.PROYECTOS_EDITAR,
        Permission.PROYECTOS_ELIMINAR,
        Permission.CONTRATOS_VER_TODOS,
        Permission.CONTRATOS_CREAR,
        Permission.CONTRATOS_EDITAR,
        Permission.CONTRATOS_ELIMINAR,
        Permission.DOTACION_VER_TODOS,
        Permission.DOTACION_GESTIONAR,
        Permission.CICLOS_VER,
        Permission.CICLOS_CREAR,
        Permission.CICLOS_EDITAR,
        Permission.CICLOS_ELIMINAR,
        Permission.ASIGNACIONES_VER,
        Permission.ASIGNACIONES_GESTIONAR,
        Permission.EMPRESAS_GESTIONAR,
        Permission.SERVICIOS_GESTIONAR,
        Permission.REPORTES_GLOBALES,
    ],
    RolUsuario.JEFE_PROYECTO: [
        Permission.PROYECTOS_EDITAR,  # Solo sus proyectos
        Permission.CONTRATOS_CREAR,
        Permission.CONTRATOS_EDITAR,
        Permission.DOTACION_GESTIONAR,
        Permission.CICLOS_VER,
        Permission.CICLOS_CREAR,
        Permission.CICLOS_EDITAR,
        Permission.ASIGNACIONES_VER,
        Permission.ASIGNACIONES_GESTIONAR,
    ],
    RolUsuario.CONTRATISTA: [
        Permission.CICLOS_VER,
        Permission.ASIGNACIONES_VER,
    ],
}


def has_permission(rol: RolUsuario, permission: Permission) -> bool:
    """
    Verifica si un rol tiene un permiso especifico.

    Args:
        rol: Rol del usuario
        permission: Permiso a verificar

    Returns:
        True si tiene el permiso, False en caso contrario
    """
    return permission in ROLE_PERMISSIONS.get(rol, [])


def has_any_permission(rol: RolUsuario, permissions: List[Permission]) -> bool:
    """
    Verifica si un rol tiene al menos uno de los permisos.

    Args:
        rol: Rol del usuario
        permissions: Lista de permisos a verificar

    Returns:
        True si tiene al menos uno, False en caso contrario
    """
    user_permissions = ROLE_PERMISSIONS.get(rol, [])
    return any(p in user_permissions for p in permissions)


def require_permission(rol: RolUsuario, permission: Permission) -> None:
    """
    Requiere que el usuario tenga un permiso especifico.
    Lanza HTTPException 403 si no lo tiene.

    Args:
        rol: Rol del usuario
        permission: Permiso requerido

    Raises:
        HTTPException: Si no tiene el permiso
    """
    if not has_permission(rol, permission):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"No tiene permiso para realizar esta accion: {permission.value}",
        )


def require_roles(rol: RolUsuario, allowed_roles: List[RolUsuario]) -> None:
    """
    Requiere que el usuario tenga uno de los roles permitidos.
    Lanza HTTPException 403 si no lo tiene.

    Args:
        rol: Rol del usuario
        allowed_roles: Lista de roles permitidos

    Raises:
        HTTPException: Si no tiene uno de los roles
    """
    if rol not in allowed_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene el rol necesario para realizar esta accion",
        )
