"""
Script para importar datos desde CSV a la base de datos.

Uso:
    python -m app.db.import_data

Este script:
1. Lee el CSV de datos anonimizados
2. Crea cargos faltantes
3. Inserta trabajadores unicos (por RUT)
4. Crea ciclos de turno
5. Crea asignaciones trabajador-ciclo
6. Calcula requerimientos por cargo/ciclo
"""

import csv
import os
from collections import defaultdict
from datetime import datetime
from pathlib import Path

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.config import get_settings
from app.models.asignacion import Asignacion, Requerimiento
from app.models.cargo import Cargo
from app.models.ciclo import Ciclo
from app.models.contrato import Contrato
from app.models.empresa import Empresa
from app.models.proyecto import Proyecto
from app.models.trabajador import Trabajador


def normalizar_cargo(nombre: str) -> str:
    """Convierte 'PERFORISTA DE SONDAJE' a 'Perforista De Sondaje'"""
    return nombre.strip().title()


def get_or_create_cargo(
    session,
    nombre_normalizado: str,
    proyecto_id: int,
    empresa_id: int,
    cargos_cache: dict,
) -> int:
    """Obtiene o crea un cargo, retorna su ID"""
    key = (nombre_normalizado.lower(), proyecto_id, empresa_id)

    if key in cargos_cache:
        return cargos_cache[key]

    # Buscar en DB
    cargo = (
        session.query(Cargo)
        .filter(
            Cargo.nombre.ilike(nombre_normalizado),
            Cargo.proyecto_id == proyecto_id,
            Cargo.empresa_id == empresa_id,
        )
        .first()
    )

    if cargo:
        cargos_cache[key] = cargo.id
        return cargo.id

    # Crear nuevo cargo
    nuevo_cargo = Cargo(
        nombre=nombre_normalizado,
        proyecto_id=proyecto_id,
        empresa_id=empresa_id,
        nivel="OPERATIVO",
    )
    session.add(nuevo_cargo)
    session.flush()  # Para obtener el ID
    cargos_cache[key] = nuevo_cargo.id
    print(
        f"  + Cargo creado: {nombre_normalizado} (proyecto={proyecto_id}, empresa={empresa_id})"
    )
    return nuevo_cargo.id


def main():
    print("=" * 60)
    print("IMPORTACION DE DATOS DESDE CSV")
    print("=" * 60)

    # Configuracion
    settings = get_settings()
    engine = create_engine(settings.database_url)
    Session = sessionmaker(bind=engine)
    session = Session()

    # Ruta del CSV
    csv_path = Path(__file__).parent / "data" / "datos-anonimizados.csv"
    if not csv_path.exists():
        print(f"ERROR: No se encontro el archivo {csv_path}")
        return

    print(f"\nLeyendo: {csv_path}")

    try:
        # Cargar mapeos existentes
        print("\n1. Cargando datos existentes...")

        # Empresas: nombre -> id
        empresas_map = {}
        for empresa in session.query(Empresa).all():
            empresas_map[empresa.nombre] = empresa.id
            # Mapeo adicional sin "SpA", "Ltda", "S.A."
            nombre_simple = (
                empresa.nombre.replace(" SpA", "")
                .replace(" Ltda", "")
                .replace(" S.A.", "")
            )
            empresas_map[nombre_simple] = empresa.id
        print(f"   Empresas: {len(empresas_map)} mapeos")

        # Proyectos: nombre -> id
        proyectos_map = {}
        for proyecto in session.query(Proyecto).all():
            proyectos_map[proyecto.nombre] = proyecto.id
            # Mapeo sin "Proyecto "
            nombre_simple = proyecto.nombre.replace("Proyecto ", "")
            proyectos_map[nombre_simple] = proyecto.id
        print(f"   Proyectos: {len(proyectos_map)} mapeos")

        # Contratos: (proyecto_id, empresa_id) -> contrato_id
        contratos_map = {}
        for contrato in session.query(Contrato).all():
            contratos_map[(contrato.proyecto_id, contrato.empresa_id)] = contrato.id
        print(f"   Contratos: {len(contratos_map)} registros")

        # Cache de cargos existentes
        cargos_cache = {}
        for cargo in session.query(Cargo).all():
            key = (cargo.nombre.lower(), cargo.proyecto_id, cargo.empresa_id)
            cargos_cache[key] = cargo.id
        print(f"   Cargos existentes: {len(cargos_cache)}")

        # Leer CSV
        print("\n2. Procesando CSV...")
        trabajadores_unicos = {}  # rut -> datos
        ciclos_unicos = {}  # (contrato_id, letra, fecha_inicio, fecha_fin) -> datos
        asignaciones_pendientes = []  # Lista de (rut, ciclo_key)
        requerimientos_contador = defaultdict(
            lambda: defaultdict(int)
        )  # ciclo_key -> cargo_id -> count

        with open(csv_path, "r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            rows_procesadas = 0
            rows_saltadas = 0

            for row in reader:
                try:
                    # Obtener IDs de empresa y proyecto
                    empresa_nombre = row["EMPRESA"].strip()
                    proyecto_nombre = row["PROYECTO"].strip()

                    empresa_id = empresas_map.get(empresa_nombre)
                    proyecto_id = proyectos_map.get(
                        proyecto_nombre
                    ) or proyectos_map.get(proyecto_nombre.replace("Proyecto ", ""))

                    if not empresa_id:
                        rows_saltadas += 1
                        continue
                    if not proyecto_id:
                        rows_saltadas += 1
                        continue

                    # Obtener contrato
                    contrato_key = (proyecto_id, empresa_id)
                    contrato_id = contratos_map.get(contrato_key)

                    if not contrato_id:
                        rows_saltadas += 1
                        continue

                    # Cargo
                    cargo_nombre = normalizar_cargo(row["CARGO TRABAJADOR"])
                    cargo_id = get_or_create_cargo(
                        session, cargo_nombre, proyecto_id, empresa_id, cargos_cache
                    )

                    # Trabajador
                    rut = row["RUT"].strip()
                    if rut not in trabajadores_unicos:
                        trabajadores_unicos[rut] = {
                            "rut": rut,
                            "nombres": row["NOMBRES"].strip(),
                            "apellidos": row["APELLIDOS"].strip(),
                            "email": row["MAIL"].strip() if row["MAIL"] else None,
                            "empresa_id": empresa_id,
                            "proyecto_id": proyecto_id,
                            "cargo_id": cargo_id,
                        }

                    # Ciclo
                    turno = row["TURNO"].strip()
                    fecha_inicio = row["FECHA INGRESO TURNO"].strip()
                    fecha_fin = row["FECHA SALIDA TURNO"].strip()

                    ciclo_key = (contrato_id, turno, fecha_inicio, fecha_fin)
                    if ciclo_key not in ciclos_unicos:
                        ciclos_unicos[ciclo_key] = {
                            "contrato_id": contrato_id,
                            "letra": turno,
                            "fecha_inicio": datetime.strptime(
                                fecha_inicio, "%Y-%m-%d"
                            ).date(),
                            "fecha_fin": datetime.strptime(
                                fecha_fin, "%Y-%m-%d"
                            ).date(),
                        }

                    # Asignacion pendiente
                    asignaciones_pendientes.append((rut, ciclo_key, cargo_id))

                    # Contador de requerimientos
                    requerimientos_contador[ciclo_key][cargo_id] += 1

                    rows_procesadas += 1
                except Exception as e:
                    print(f"   Error en fila: {e}")
                    rows_saltadas += 1

        print(f"   Filas procesadas: {rows_procesadas}")
        print(f"   Filas saltadas: {rows_saltadas}")
        print(f"   Trabajadores unicos: {len(trabajadores_unicos)}")
        print(f"   Ciclos unicos: {len(ciclos_unicos)}")

        # Insertar trabajadores
        print("\n3. Insertando trabajadores...")
        trabajador_id_map = {}  # rut -> id

        for rut, datos in trabajadores_unicos.items():
            # Verificar si ya existe
            existente = session.query(Trabajador).filter(Trabajador.rut == rut).first()
            if existente:
                trabajador_id_map[rut] = existente.id
                continue

            trabajador = Trabajador(
                rut=datos["rut"],
                nombres=datos["nombres"],
                apellidos=datos["apellidos"],
                email=datos["email"],
                empresa_id=datos["empresa_id"],
                proyecto_id=datos["proyecto_id"],
                cargo_id=datos["cargo_id"],
                activo=True,
            )
            session.add(trabajador)
            session.flush()
            trabajador_id_map[rut] = trabajador.id

        print(f"   Trabajadores insertados: {len(trabajadores_unicos)}")

        # Insertar ciclos
        print("\n4. Insertando ciclos...")
        ciclo_id_map = {}  # ciclo_key -> id

        for ciclo_key, datos in ciclos_unicos.items():
            # Verificar si ya existe
            existente = (
                session.query(Ciclo)
                .filter(
                    Ciclo.contrato_id == datos["contrato_id"],
                    Ciclo.letra == datos["letra"],
                    Ciclo.fecha_inicio == datos["fecha_inicio"],
                    Ciclo.fecha_fin == datos["fecha_fin"],
                )
                .first()
            )

            if existente:
                ciclo_id_map[ciclo_key] = existente.id
                continue

            ciclo = Ciclo(
                contrato_id=datos["contrato_id"],
                letra=datos["letra"],
                fecha_inicio=datos["fecha_inicio"],
                fecha_fin=datos["fecha_fin"],
                estado="NO_DEFINIDO",
                horario="DIA",
            )
            session.add(ciclo)
            session.flush()
            ciclo_id_map[ciclo_key] = ciclo.id

        print(f"   Ciclos insertados: {len(ciclos_unicos)}")

        # Insertar asignaciones
        print("\n5. Insertando asignaciones...")
        asignaciones_insertadas = 0
        asignaciones_existentes = set()

        # Cargar asignaciones existentes
        for asig in session.query(Asignacion).all():
            asignaciones_existentes.add((asig.ciclo_id, asig.trabajador_id))

        for rut, ciclo_key, cargo_id in asignaciones_pendientes:
            trabajador_id = trabajador_id_map.get(rut)
            ciclo_id = ciclo_id_map.get(ciclo_key)

            if not trabajador_id or not ciclo_id:
                continue

            if (ciclo_id, trabajador_id) in asignaciones_existentes:
                continue

            asignacion = Asignacion(ciclo_id=ciclo_id, trabajador_id=trabajador_id)
            session.add(asignacion)
            asignaciones_existentes.add((ciclo_id, trabajador_id))
            asignaciones_insertadas += 1

        print(f"   Asignaciones insertadas: {asignaciones_insertadas}")

        # Insertar requerimientos
        print("\n6. Calculando requerimientos...")
        requerimientos_insertados = 0

        for ciclo_key, cargos in requerimientos_contador.items():
            ciclo_id = ciclo_id_map.get(ciclo_key)
            if not ciclo_id:
                continue

            for cargo_id, cantidad in cargos.items():
                # Verificar si ya existe
                existente = (
                    session.query(Requerimiento)
                    .filter(
                        Requerimiento.ciclo_id == ciclo_id,
                        Requerimiento.cargo_id == cargo_id,
                    )
                    .first()
                )

                if existente:
                    # Actualizar cantidad
                    existente.cantidad_necesaria = cantidad
                else:
                    req = Requerimiento(
                        ciclo_id=ciclo_id,
                        cargo_id=cargo_id,
                        cantidad_necesaria=cantidad,
                    )
                    session.add(req)
                    requerimientos_insertados += 1

        print(f"   Requerimientos insertados: {requerimientos_insertados}")

        # Commit final
        print("\n7. Guardando cambios...")
        session.commit()
        print("   Cambios guardados exitosamente!")

        # Resumen final
        print("\n" + "=" * 60)
        print("RESUMEN DE IMPORTACION")
        print("=" * 60)

        counts = {}
        for table in [
            "trabajadores",
            "ciclos",
            "asignaciones",
            "requerimientos",
            "cargos",
        ]:
            result = session.execute(text(f"SELECT COUNT(*) FROM {table}"))
            counts[table] = result.scalar()

        for table, count in counts.items():
            print(f"  {table}: {count} registros")

    except Exception as e:
        print(f"\nERROR: {e}")
        session.rollback()
        raise
    finally:
        session.close()


if __name__ == "__main__":
    main()
