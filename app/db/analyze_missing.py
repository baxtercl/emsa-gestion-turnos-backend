"""
Script para analizar combinaciones proyecto-empresa faltantes en el CSV.
"""

import csv
from collections import defaultdict
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.config import get_settings
from app.models.contrato import Contrato
from app.models.empresa import Empresa
from app.models.proyecto import Proyecto


def main():
    settings = get_settings()
    engine = create_engine(settings.database_url)
    Session = sessionmaker(bind=engine)
    session = Session()

    # Cargar mapeos
    empresas_map = {}
    for empresa in session.query(Empresa).all():
        empresas_map[empresa.nombre] = empresa.id
        nombre_simple = (
            empresa.nombre.replace(" SpA", "").replace(" Ltda", "").replace(" S.A.", "")
        )
        empresas_map[nombre_simple] = empresa.id

    proyectos_map = {}
    for proyecto in session.query(Proyecto).all():
        proyectos_map[proyecto.nombre] = proyecto.id
        nombre_simple = proyecto.nombre.replace("Proyecto ", "")
        proyectos_map[nombre_simple] = proyecto.id

    # Contratos existentes
    contratos_existentes = set()
    for contrato in session.query(Contrato).all():
        contratos_existentes.add((contrato.proyecto_id, contrato.empresa_id))

    # Leer CSV y encontrar combinaciones
    csv_path = Path(__file__).parent / "data" / "datos-anonimizados.csv"
    combinaciones_csv = defaultdict(int)

    with open(csv_path, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            empresa_nombre = row["EMPRESA"].strip()
            proyecto_nombre = row["PROYECTO"].strip()

            empresa_id = empresas_map.get(empresa_nombre)
            proyecto_id = proyectos_map.get(proyecto_nombre) or proyectos_map.get(
                proyecto_nombre.replace("Proyecto ", "")
            )

            if empresa_id and proyecto_id:
                combinaciones_csv[
                    (proyecto_id, empresa_id, proyecto_nombre, empresa_nombre)
                ] += 1

    print("=" * 70)
    print("ANALISIS DE CONTRATOS")
    print("=" * 70)

    print("\n1. CONTRATOS EXISTENTES EN DB:")
    for pid, eid in sorted(contratos_existentes):
        print(f"   Proyecto {pid} + Empresa {eid}")

    print("\n2. COMBINACIONES EN CSV:")
    faltantes = []
    for (pid, eid, pnombre, enombre), count in sorted(combinaciones_csv.items()):
        existe = (pid, eid) in contratos_existentes
        status = "OK" if existe else "FALTA"
        print(
            f"   [{status}] Proyecto {pid} ({pnombre}) + Empresa {eid} ({enombre}): {count} filas"
        )
        if not existe:
            faltantes.append((pid, eid, pnombre, enombre, count))

    print("\n3. CONTRATOS FALTANTES:")
    if faltantes:
        for pid, eid, pnombre, enombre, count in faltantes:
            print(f"   - Proyecto {pid} + Empresa {eid} ({count} filas)")
            print(f"     {pnombre} <-> {enombre}")
    else:
        print("   Ninguno - todos los contratos existen!")

    print("\n4. SQL PARA CREAR CONTRATOS FALTANTES:")
    if faltantes:
        print(
            "   INSERT INTO contratos (proyecto_id, servicio_id, empresa_id, tipo_turnos, patron, activo) VALUES"
        )
        values = []
        for pid, eid, _, _, _ in faltantes:
            # servicio_id=1 como default (Sondajes)
            values.append(f"   ({pid}, 1, {eid}, 'ABCD', '7x7', true)")
        print(",\n".join(values) + ";")

    session.close()


if __name__ == "__main__":
    main()
