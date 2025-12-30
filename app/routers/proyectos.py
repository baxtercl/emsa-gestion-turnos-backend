"""
Router de proyectos
"""

from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import (Asignacion, Cargo, Ciclo, Contrato, Proyecto,
                        Requerimiento, Trabajador, Usuario)
from app.models.usuario import RolUsuario
from app.routers.auth import get_current_user
from app.schemas.cargo import CargoListResponse, CargoResponse, CargoTreeNode
from app.schemas.ciclo import (CicloCalendarioEvento, CicloCalendarioResponse,
                               CicloListResponse, CicloResponse,
                               CoberturaResponse)
from app.schemas.contrato import ContratoListResponse, ContratoResponse
from app.schemas.proyecto import (AlertaResponse, ContratoResumenResponse,
                                  PanelMandanteResponse, ProyectoListResponse,
                                  ProyectoResponse, StatsResponse)
from app.schemas.trabajador import (TrabajadorCreate, TrabajadorListResponse,
                                    TrabajadorResponse)

router = APIRouter()

# Colores para turnos
TURNO_COLORS = {
    "A": "#4a7bc1",  # Azul
    "B": "#5fad43",  # Verde
    "C": "#f5a02b",  # Naranja
    "D": "#f13a5c",  # Rojo
}


@router.get("", response_model=ProyectoListResponse)
async def get_proyectos(
    current_user: Annotated[Usuario, Depends(get_current_user)],
    db: Session = Depends(get_db),
    activo: bool = None,
):
    """
    Lista todos los proyectos.
    Opcionalmente filtrar por estado activo.
    """
    query = db.query(Proyecto)

    if activo is not None:
        query = query.filter(Proyecto.activo == activo)

    proyectos = query.order_by(Proyecto.nombre).all()

    result = []
    for p in proyectos:
        contratos_count = (
            db.query(func.count(Contrato.id))
            .filter(Contrato.proyecto_id == p.id)
            .scalar()
        )

        trabajadores_count = (
            db.query(func.count(Trabajador.id))
            .filter(Trabajador.proyecto_id == p.id, Trabajador.activo == True)
            .scalar()
        )

        result.append(
            ProyectoResponse(
                id=p.id,
                nombre=p.nombre,
                descripcion=p.descripcion,
                activo=p.activo,
                fecha_inicio=p.fecha_inicio,
                fecha_fin=p.fecha_fin,
                contratos_count=contratos_count,
                trabajadores_count=trabajadores_count,
                created_at=p.created_at,
                updated_at=p.updated_at,
            )
        )

    return ProyectoListResponse(data=result)


@router.get("/{proyecto_id}", response_model=ProyectoResponse)
async def get_proyecto(
    proyecto_id: int,
    current_user: Annotated[Usuario, Depends(get_current_user)],
    db: Session = Depends(get_db),
):
    """
    Obtiene un proyecto por ID.
    """
    proyecto = db.query(Proyecto).filter(Proyecto.id == proyecto_id).first()

    if not proyecto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Proyecto no encontrado"
        )

    contratos_count = (
        db.query(func.count(Contrato.id))
        .filter(Contrato.proyecto_id == proyecto.id)
        .scalar()
    )

    trabajadores_count = (
        db.query(func.count(Trabajador.id))
        .filter(Trabajador.proyecto_id == proyecto.id, Trabajador.activo == True)
        .scalar()
    )

    return ProyectoResponse(
        id=proyecto.id,
        nombre=proyecto.nombre,
        descripcion=proyecto.descripcion,
        activo=proyecto.activo,
        fecha_inicio=proyecto.fecha_inicio,
        fecha_fin=proyecto.fecha_fin,
        contratos_count=contratos_count,
        trabajadores_count=trabajadores_count,
        created_at=proyecto.created_at,
        updated_at=proyecto.updated_at,
    )


@router.get("/{proyecto_id}/contratos", response_model=ContratoListResponse)
async def get_proyecto_contratos(
    proyecto_id: int,
    current_user: Annotated[Usuario, Depends(get_current_user)],
    db: Session = Depends(get_db),
):
    """
    Lista los contratos de un proyecto.
    """
    proyecto = db.query(Proyecto).filter(Proyecto.id == proyecto_id).first()
    if not proyecto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Proyecto no encontrado"
        )

    contratos = db.query(Contrato).filter(Contrato.proyecto_id == proyecto_id).all()

    result = []
    for c in contratos:
        result.append(
            ContratoResponse(
                id=c.id,
                proyecto_id=c.proyecto_id,
                servicio_id=c.servicio_id,
                empresa_id=c.empresa_id,
                tipo_turnos=c.tipo_turnos.value if c.tipo_turnos else None,
                patron=c.patron,
                activo=c.activo,
                fecha_inicio=c.fecha_inicio,
                fecha_fin=c.fecha_fin,
                empresa_nombre=c.empresa.nombre if c.empresa else None,
                servicio_nombre=c.servicio.nombre if c.servicio else None,
                created_at=c.created_at,
                updated_at=c.updated_at,
            )
        )

    return ContratoListResponse(data=result)


@router.get("/{proyecto_id}/cargos", response_model=CargoListResponse)
async def get_proyecto_cargos(
    proyecto_id: int,
    current_user: Annotated[Usuario, Depends(get_current_user)],
    db: Session = Depends(get_db),
):
    """
    Lista los cargos de un proyecto.
    """
    proyecto = db.query(Proyecto).filter(Proyecto.id == proyecto_id).first()
    if not proyecto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Proyecto no encontrado"
        )

    cargos = (
        db.query(Cargo)
        .filter(Cargo.proyecto_id == proyecto_id)
        .order_by(Cargo.nivel, Cargo.nombre)
        .all()
    )

    result = []
    for c in cargos:
        # Contar subordinados
        subordinados_count = (
            db.query(func.count(Cargo.id))
            .filter(Cargo.jefe_directo_id == c.id)
            .scalar()
        )

        # Nombre del jefe directo
        jefe_nombre = None
        if c.jefe_directo_id:
            jefe = db.query(Cargo).filter(Cargo.id == c.jefe_directo_id).first()
            if jefe:
                jefe_nombre = jefe.nombre

        result.append(
            CargoResponse(
                id=c.id,
                nombre=c.nombre,
                proyecto_id=c.proyecto_id,
                empresa_id=c.empresa_id,
                empresa_nombre=c.empresa.nombre if c.empresa else None,
                jefe_directo_id=c.jefe_directo_id,
                jefe_directo_nombre=jefe_nombre,
                nivel=c.nivel,
                subordinados_count=subordinados_count,
                created_at=c.created_at,
                updated_at=c.updated_at,
            )
        )

    return CargoListResponse(data=result)


@router.get("/{proyecto_id}/cargos/tree")
async def get_proyecto_cargos_tree(
    proyecto_id: int,
    current_user: Annotated[Usuario, Depends(get_current_user)],
    db: Session = Depends(get_db),
):
    """
    Obtiene el organigrama en estructura de arbol.
    """
    proyecto = db.query(Proyecto).filter(Proyecto.id == proyecto_id).first()
    if not proyecto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Proyecto no encontrado"
        )

    cargos = db.query(Cargo).filter(Cargo.proyecto_id == proyecto_id).all()

    # Crear diccionario de cargos
    cargo_dict = {c.id: c for c in cargos}

    def build_tree(cargo_id: int) -> CargoTreeNode:
        cargo = cargo_dict.get(cargo_id)
        if not cargo:
            return None

        children = [build_tree(c.id) for c in cargos if c.jefe_directo_id == cargo_id]

        return CargoTreeNode(
            id=cargo.id,
            nombre=cargo.nombre,
            nivel=cargo.nivel,
            empresa_nombre=cargo.empresa.nombre if cargo.empresa else None,
            children=[c for c in children if c is not None],
        )

    # Encontrar nodos raiz (sin jefe directo)
    roots = [c for c in cargos if c.jefe_directo_id is None]

    if not roots:
        return {"data": None}

    # Si hay multiples raices, crear nodo virtual
    if len(roots) == 1:
        tree = build_tree(roots[0].id)
    else:
        tree = CargoTreeNode(
            id=0,
            nombre=proyecto.nombre,
            nivel="PROYECTO",
            empresa_nombre=None,
            children=[build_tree(r.id) for r in roots if build_tree(r.id)],
        )

    return {"data": tree}


@router.get("/{proyecto_id}/trabajadores", response_model=TrabajadorListResponse)
async def get_proyecto_trabajadores(
    proyecto_id: int,
    current_user: Annotated[Usuario, Depends(get_current_user)],
    db: Session = Depends(get_db),
    activo: bool = None,
):
    """
    Lista los trabajadores de un proyecto.
    """
    proyecto = db.query(Proyecto).filter(Proyecto.id == proyecto_id).first()
    if not proyecto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Proyecto no encontrado"
        )

    query = db.query(Trabajador).filter(Trabajador.proyecto_id == proyecto_id)

    if activo is not None:
        query = query.filter(Trabajador.activo == activo)

    trabajadores = query.order_by(Trabajador.apellidos, Trabajador.nombres).all()

    result = []
    for t in trabajadores:
        # Contar asignaciones activas
        hoy = date.today()
        asignaciones_activas = (
            db.query(func.count(Asignacion.id))
            .join(Ciclo, Asignacion.ciclo_id == Ciclo.id)
            .filter(
                Asignacion.trabajador_id == t.id,
                Ciclo.fecha_inicio <= hoy,
                Ciclo.fecha_fin >= hoy,
            )
            .scalar()
        )

        result.append(
            TrabajadorResponse(
                id=t.id,
                rut=t.rut,
                nombres=t.nombres,
                apellidos=t.apellidos,
                nombre_completo=f"{t.nombres} {t.apellidos}",
                email=t.email,
                telefono=t.telefono,
                proyecto_id=t.proyecto_id,
                empresa_id=t.empresa_id,
                empresa_nombre=t.empresa.nombre if t.empresa else None,
                cargo_id=t.cargo_id,
                cargo_nombre=t.cargo.nombre if t.cargo else None,
                activo=t.activo,
                fecha_ingreso=t.fecha_ingreso,
                asignaciones_activas=asignaciones_activas,
                created_at=t.created_at,
                updated_at=t.updated_at,
            )
        )

    return TrabajadorListResponse(data=result)


def require_admin_or_gestor(current_user: Usuario) -> None:
    """Verifica que el usuario sea ADMIN o GESTOR_PROYECTOS"""
    if current_user.rol not in [RolUsuario.ADMIN, RolUsuario.GESTOR_PROYECTOS]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requieren permisos de administrador o gestor de proyectos",
        )


@router.post(
    "/{proyecto_id}/trabajadores",
    response_model=TrabajadorResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_trabajador(
    proyecto_id: int,
    trabajador_data: TrabajadorCreate,
    current_user: Annotated[Usuario, Depends(get_current_user)],
    db: Session = Depends(get_db),
):
    """
    Crea un nuevo trabajador en un proyecto.
    Solo usuarios ADMIN o GESTOR_PROYECTOS pueden crear trabajadores.
    """
    require_admin_or_gestor(current_user)

    # Verificar que el proyecto exista
    proyecto = db.query(Proyecto).filter(Proyecto.id == proyecto_id).first()
    if not proyecto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Proyecto no encontrado"
        )

    # Verificar que el RUT no exista
    if db.query(Trabajador).filter(Trabajador.rut == trabajador_data.rut).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe un trabajador con este RUT",
        )

    # Verificar que la empresa exista
    from app.models import Empresa

    empresa = db.query(Empresa).filter(Empresa.id == trabajador_data.empresa_id).first()
    if not empresa:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La empresa especificada no existe",
        )

    # Verificar que el cargo exista si se proporciona
    if trabajador_data.cargo_id:
        cargo = db.query(Cargo).filter(Cargo.id == trabajador_data.cargo_id).first()
        if not cargo:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El cargo especificado no existe",
            )

    # Crear trabajador
    nuevo_trabajador = Trabajador(
        rut=trabajador_data.rut,
        nombres=trabajador_data.nombres,
        apellidos=trabajador_data.apellidos,
        email=trabajador_data.email,
        telefono=trabajador_data.telefono,
        proyecto_id=proyecto_id,
        empresa_id=trabajador_data.empresa_id,
        cargo_id=trabajador_data.cargo_id,
        fecha_ingreso=trabajador_data.fecha_ingreso,
        activo=True,
    )

    db.add(nuevo_trabajador)
    db.commit()
    db.refresh(nuevo_trabajador)

    return TrabajadorResponse(
        id=nuevo_trabajador.id,
        rut=nuevo_trabajador.rut,
        nombres=nuevo_trabajador.nombres,
        apellidos=nuevo_trabajador.apellidos,
        nombre_completo=f"{nuevo_trabajador.nombres} {nuevo_trabajador.apellidos}",
        email=nuevo_trabajador.email,
        telefono=nuevo_trabajador.telefono,
        proyecto_id=nuevo_trabajador.proyecto_id,
        empresa_id=nuevo_trabajador.empresa_id,
        empresa_nombre=(
            nuevo_trabajador.empresa.nombre if nuevo_trabajador.empresa else None
        ),
        cargo_id=nuevo_trabajador.cargo_id,
        cargo_nombre=nuevo_trabajador.cargo.nombre if nuevo_trabajador.cargo else None,
        activo=nuevo_trabajador.activo,
        fecha_ingreso=nuevo_trabajador.fecha_ingreso,
        created_at=nuevo_trabajador.created_at,
        updated_at=nuevo_trabajador.updated_at,
    )


@router.get("/{proyecto_id}/ciclos", response_model=CicloListResponse)
async def get_proyecto_ciclos(
    proyecto_id: int,
    current_user: Annotated[Usuario, Depends(get_current_user)],
    db: Session = Depends(get_db),
):
    """
    Lista los ciclos de todos los contratos del proyecto.
    """
    proyecto = db.query(Proyecto).filter(Proyecto.id == proyecto_id).first()
    if not proyecto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Proyecto no encontrado"
        )

    ciclos = (
        db.query(Ciclo)
        .join(Contrato, Ciclo.contrato_id == Contrato.id)
        .filter(Contrato.proyecto_id == proyecto_id)
        .order_by(Ciclo.fecha_inicio)
        .all()
    )

    result = []
    for c in ciclos:
        # Calcular cobertura
        total_requerido = (
            db.query(func.coalesce(func.sum(Requerimiento.cantidad_necesaria), 0))
            .filter(Requerimiento.ciclo_id == c.id)
            .scalar()
        )

        total_asignado = (
            db.query(func.count(Asignacion.id))
            .filter(Asignacion.ciclo_id == c.id)
            .scalar()
        )

        cobertura = None
        if total_requerido > 0:
            cobertura = CoberturaResponse(
                requeridos=total_requerido,
                asignados=total_asignado,
                porcentaje=round((total_asignado / total_requerido) * 100, 1),
            )

        result.append(
            CicloResponse(
                id=c.id,
                contrato_id=c.contrato_id,
                letra=c.letra,
                fecha_inicio=c.fecha_inicio,
                fecha_fin=c.fecha_fin,
                estado=c.estado.value if c.estado else "NO_DEFINIDO",
                horario=c.horario,
                cobertura=cobertura,
                created_at=c.created_at,
                updated_at=c.updated_at,
            )
        )

    return CicloListResponse(data=result)


@router.get("/{proyecto_id}/ciclos/calendario", response_model=CicloCalendarioResponse)
async def get_proyecto_ciclos_calendario(
    proyecto_id: int,
    current_user: Annotated[Usuario, Depends(get_current_user)],
    db: Session = Depends(get_db),
):
    """
    Obtiene los ciclos en formato de eventos para FullCalendar.
    """
    proyecto = db.query(Proyecto).filter(Proyecto.id == proyecto_id).first()
    if not proyecto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Proyecto no encontrado"
        )

    ciclos = (
        db.query(Ciclo)
        .join(Contrato, Ciclo.contrato_id == Contrato.id)
        .filter(Contrato.proyecto_id == proyecto_id)
        .order_by(Ciclo.fecha_inicio)
        .all()
    )

    eventos = []
    for c in ciclos:
        eventos.append(
            CicloCalendarioEvento(
                id=str(c.id),
                title=f"Turno {c.letra}",
                start=c.fecha_inicio.isoformat(),
                end=c.fecha_fin.isoformat(),
                color=TURNO_COLORS.get(c.letra, "#666666"),
                extendedProps={
                    "ciclo_id": c.id,
                    "contrato_id": c.contrato_id,
                    "estado": c.estado.value if c.estado else "NO_DEFINIDO",
                    "letra": c.letra,
                },
            )
        )

    return CicloCalendarioResponse(data=eventos)


@router.get("/{proyecto_id}/panel-mandante", response_model=PanelMandanteResponse)
async def get_panel_mandante(
    proyecto_id: int,
    current_user: Annotated[Usuario, Depends(get_current_user)],
    db: Session = Depends(get_db),
):
    """
    Obtiene el panel resumen para el mandante.
    """
    proyecto = db.query(Proyecto).filter(Proyecto.id == proyecto_id).first()
    if not proyecto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Proyecto no encontrado"
        )

    contratos = (
        db.query(Contrato)
        .filter(Contrato.proyecto_id == proyecto_id, Contrato.activo == True)
        .all()
    )

    resumen_contratos = []
    alertas = []
    hoy = date.today()

    for contrato in contratos:
        # Buscar ciclo actual
        ciclo_actual = (
            db.query(Ciclo)
            .filter(
                Ciclo.contrato_id == contrato.id,
                Ciclo.fecha_inicio <= hoy,
                Ciclo.fecha_fin >= hoy,
            )
            .first()
        )

        # Calcular dotacion
        dotacion_requerida = 0
        dotacion_asignada = 0

        if ciclo_actual:
            dotacion_requerida = (
                db.query(func.coalesce(func.sum(Requerimiento.cantidad_necesaria), 0))
                .filter(Requerimiento.ciclo_id == ciclo_actual.id)
                .scalar()
            )

            dotacion_asignada = (
                db.query(func.count(Asignacion.id))
                .filter(Asignacion.ciclo_id == ciclo_actual.id)
                .scalar()
            )

            # Generar alertas
            if dotacion_requerida > 0:
                porcentaje = (dotacion_asignada / dotacion_requerida) * 100
                if porcentaje < 80:
                    alertas.append(
                        AlertaResponse(
                            tipo="danger",
                            mensaje=f"Cobertura crítica ({porcentaje:.0f}%) en {contrato.empresa.nombre}",
                            contrato_id=contrato.id,
                        )
                    )
                elif porcentaje < 100:
                    alertas.append(
                        AlertaResponse(
                            tipo="warning",
                            mensaje=f"Cobertura incompleta ({porcentaje:.0f}%) en {contrato.empresa.nombre}",
                            contrato_id=contrato.id,
                        )
                    )

        resumen_contratos.append(
            ContratoResumenResponse(
                contrato_id=contrato.id,
                empresa=contrato.empresa.nombre if contrato.empresa else "Sin empresa",
                servicio=(
                    contrato.servicio.nombre if contrato.servicio else "Sin servicio"
                ),
                patron=contrato.patron,
                tipo_turnos=(
                    contrato.tipo_turnos.value if contrato.tipo_turnos else "ABCD"
                ),
                ciclo_actual=(
                    {
                        "id": ciclo_actual.id,
                        "letra": ciclo_actual.letra,
                        "fecha_inicio": ciclo_actual.fecha_inicio.isoformat(),
                        "fecha_fin": ciclo_actual.fecha_fin.isoformat(),
                        "estado": ciclo_actual.estado.value,
                    }
                    if ciclo_actual
                    else None
                ),
                dotacion_requerida=dotacion_requerida,
                dotacion_asignada=dotacion_asignada,
            )
        )

    # Estadisticas generales
    total_trabajadores = (
        db.query(func.count(Trabajador.id))
        .filter(Trabajador.proyecto_id == proyecto_id, Trabajador.activo == True)
        .scalar()
    )

    # Trabajadores asignados a algun ciclo activo
    trabajadores_asignados = (
        db.query(func.count(func.distinct(Asignacion.trabajador_id)))
        .join(Ciclo, Asignacion.ciclo_id == Ciclo.id)
        .join(Contrato, Ciclo.contrato_id == Contrato.id)
        .filter(
            Contrato.proyecto_id == proyecto_id,
            Ciclo.fecha_inicio <= hoy,
            Ciclo.fecha_fin >= hoy,
        )
        .scalar()
    )

    return PanelMandanteResponse(
        proyecto={"id": proyecto.id, "nombre": proyecto.nombre},
        resumen_contratos=resumen_contratos,
        alertas=alertas,
        stats=StatsResponse(
            total_trabajadores=total_trabajadores,
            trabajadores_asignados=trabajadores_asignados,
            total_contratos=len(contratos),
            ciclo_actual=None,
        ),
    )
