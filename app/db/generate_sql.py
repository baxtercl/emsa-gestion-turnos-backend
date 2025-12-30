"""
Script para generar archivo SQL con datos operativos desde la base de datos.

Uso:
    python -m app.db.generate_sql

Genera: sql/003_data.sql
"""

from pathlib import Path

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.config import get_settings


def escape_sql(value):
    """Escapa comillas simples para SQL"""
    if value is None:
        return "NULL"
    if isinstance(value, bool):
        return "TRUE" if value else "FALSE"
    if isinstance(value, (int, float)):
        return str(value)
    # Escapar comillas simples
    return "'" + str(value).replace("'", "''") + "'"


def main():
    print("=" * 60)
    print("GENERADOR DE SQL DESDE BASE DE DATOS")
    print("=" * 60)

    settings = get_settings()
    engine = create_engine(settings.database_url)

    output_path = Path(__file__).parent.parent.parent / "sql" / "003_data.sql"

    lines = []
    lines.append("-- ============================================================")
    lines.append("-- EMSA Gestion de Turnos - Datos Operativos")
    lines.append("-- Generado automaticamente desde la base de datos")
    lines.append("-- ============================================================")
    lines.append("")
    lines.append("-- IMPORTANTE: Ejecutar despues de 001_schema.sql y 002_seed.sql")
    lines.append("")

    with engine.connect() as conn:
        # ============================================================
        # CARGOS (solo los que no estan en 002_seed.sql, id > 14)
        # ============================================================
        lines.append("-- ============================================================")
        lines.append("-- CARGOS ADICIONALES (generados desde CSV)")
        lines.append("-- ============================================================")
        lines.append("")

        result = conn.execute(
            text(
                """
            SELECT id, nombre, proyecto_id, empresa_id, jefe_directo_id, nivel
            FROM cargos
            WHERE id > 14
            ORDER BY id
        """
            )
        )
        cargos = result.fetchall()

        if cargos:
            lines.append(
                "INSERT INTO cargos (id, nombre, proyecto_id, empresa_id, jefe_directo_id, nivel) VALUES"
            )
            values = []
            for c in cargos:
                jefe = "NULL" if c.jefe_directo_id is None else str(c.jefe_directo_id)
                values.append(
                    f"({c.id}, {escape_sql(c.nombre)}, {c.proyecto_id}, {c.empresa_id}, {jefe}, {escape_sql(c.nivel)})"
                )
            lines.append(",\n".join(values) + ";")
        lines.append("")

        # ============================================================
        # TRABAJADORES
        # ============================================================
        lines.append("-- ============================================================")
        lines.append("-- TRABAJADORES")
        lines.append("-- ============================================================")
        lines.append("")

        result = conn.execute(
            text(
                """
            SELECT id, rut, nombres, apellidos, email, telefono,
                   proyecto_id, empresa_id, cargo_id, activo, fecha_ingreso
            FROM trabajadores
            ORDER BY id
        """
            )
        )
        trabajadores = result.fetchall()

        if trabajadores:
            lines.append(
                "INSERT INTO trabajadores (id, rut, nombres, apellidos, email, telefono, proyecto_id, empresa_id, cargo_id, activo, fecha_ingreso) VALUES"
            )
            values = []
            for t in trabajadores:
                telefono = escape_sql(t.telefono)
                email = escape_sql(t.email)
                fecha = escape_sql(str(t.fecha_ingreso)) if t.fecha_ingreso else "NULL"
                values.append(
                    f"({t.id}, {escape_sql(t.rut)}, {escape_sql(t.nombres)}, {escape_sql(t.apellidos)}, {email}, {telefono}, {t.proyecto_id}, {t.empresa_id}, {t.cargo_id}, {escape_sql(t.activo)}, {fecha})"
                )
            lines.append(",\n".join(values) + ";")
        lines.append("")

        # ============================================================
        # CICLOS
        # ============================================================
        lines.append("-- ============================================================")
        lines.append("-- CICLOS")
        lines.append("-- ============================================================")
        lines.append("")

        result = conn.execute(
            text(
                """
            SELECT id, contrato_id, letra, fecha_inicio, fecha_fin, estado, horario
            FROM ciclos
            ORDER BY id
        """
            )
        )
        ciclos = result.fetchall()

        if ciclos:
            lines.append(
                "INSERT INTO ciclos (id, contrato_id, letra, fecha_inicio, fecha_fin, estado, horario) VALUES"
            )
            values = []
            for c in ciclos:
                values.append(
                    f"({c.id}, {c.contrato_id}, {escape_sql(c.letra)}, {escape_sql(str(c.fecha_inicio))}, {escape_sql(str(c.fecha_fin))}, {escape_sql(c.estado)}, {escape_sql(c.horario)})"
                )
            lines.append(",\n".join(values) + ";")
        lines.append("")

        # ============================================================
        # ASIGNACIONES
        # ============================================================
        lines.append("-- ============================================================")
        lines.append("-- ASIGNACIONES")
        lines.append("-- ============================================================")
        lines.append("")

        result = conn.execute(
            text(
                """
            SELECT id, ciclo_id, trabajador_id
            FROM asignaciones
            ORDER BY id
        """
            )
        )
        asignaciones = result.fetchall()

        if asignaciones:
            lines.append(
                "INSERT INTO asignaciones (id, ciclo_id, trabajador_id) VALUES"
            )
            values = []
            for a in asignaciones:
                values.append(f"({a.id}, {a.ciclo_id}, {a.trabajador_id})")
            lines.append(",\n".join(values) + ";")
        lines.append("")

        # ============================================================
        # REQUERIMIENTOS
        # ============================================================
        lines.append("-- ============================================================")
        lines.append("-- REQUERIMIENTOS")
        lines.append("-- ============================================================")
        lines.append("")

        result = conn.execute(
            text(
                """
            SELECT id, ciclo_id, cargo_id, cantidad_necesaria
            FROM requerimientos
            ORDER BY id
        """
            )
        )
        requerimientos = result.fetchall()

        if requerimientos:
            lines.append(
                "INSERT INTO requerimientos (id, ciclo_id, cargo_id, cantidad_necesaria) VALUES"
            )
            values = []
            for r in requerimientos:
                values.append(
                    f"({r.id}, {r.ciclo_id}, {r.cargo_id}, {r.cantidad_necesaria})"
                )
            lines.append(",\n".join(values) + ";")
        lines.append("")

        # ============================================================
        # RESET SEQUENCES
        # ============================================================
        lines.append("-- ============================================================")
        lines.append("-- RESET SEQUENCES")
        lines.append("-- ============================================================")
        lines.append("")
        lines.append(
            "SELECT setval('cargos_id_seq', (SELECT COALESCE(MAX(id), 1) FROM cargos));"
        )
        lines.append(
            "SELECT setval('trabajadores_id_seq', (SELECT COALESCE(MAX(id), 1) FROM trabajadores));"
        )
        lines.append(
            "SELECT setval('ciclos_id_seq', (SELECT COALESCE(MAX(id), 1) FROM ciclos));"
        )
        lines.append(
            "SELECT setval('asignaciones_id_seq', (SELECT COALESCE(MAX(id), 1) FROM asignaciones));"
        )
        lines.append(
            "SELECT setval('requerimientos_id_seq', (SELECT COALESCE(MAX(id), 1) FROM requerimientos));"
        )
        lines.append("")
        lines.append("-- ============================================================")
        lines.append("-- FIN DEL SCRIPT")
        lines.append("-- ============================================================")

    # Escribir archivo
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"\nArchivo generado: {output_path}")
    print(f"\nResumen:")
    print(f"  - Cargos adicionales: {len(cargos)}")
    print(f"  - Trabajadores: {len(trabajadores)}")
    print(f"  - Ciclos: {len(ciclos)}")
    print(f"  - Asignaciones: {len(asignaciones)}")
    print(f"  - Requerimientos: {len(requerimientos)}")


if __name__ == "__main__":
    main()
