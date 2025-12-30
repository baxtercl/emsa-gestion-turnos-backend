# Scripts SQL - EMSA Gestión de Turnos

Scripts para crear y poblar la base de datos PostgreSQL.

## Archivos

| Archivo | Descripción | Contenido |
|---------|-------------|-----------|
| `001_schema.sql` | Estructura de la base de datos | Tablas, tipos ENUM, índices, triggers, vistas |
| `002_seed.sql` | Datos base del sistema | Empresas, usuarios, servicios, proyectos, contratos, cargos base |
| `003_data.sql` | Datos operativos | Cargos adicionales, trabajadores, ciclos, asignaciones, requerimientos |

## Requisitos

- PostgreSQL 14+
- Base de datos creada: `emsa_gestion_turnos`
- Usuario con permisos de creación de tablas

## Ejecución

### Opción 1: Desde psql

```bash
psql -h localhost -U app_user -d emsa_gestion_turnos -f sql/001_schema.sql
psql -h localhost -U app_user -d emsa_gestion_turnos -f sql/002_seed.sql
psql -h localhost -U app_user -d emsa_gestion_turnos -f sql/003_data.sql
```

### Opción 2: Desde DBeaver

1. Conectar a la base de datos `emsa_gestion_turnos`
2. Abrir y ejecutar `001_schema.sql`
3. Abrir y ejecutar `002_seed.sql`
4. Abrir y ejecutar `003_data.sql`

### Opción 3: Script combinado

```bash
cat sql/001_schema.sql sql/002_seed.sql sql/003_data.sql | psql -h localhost -U app_user -d emsa_gestion_turnos
```

## Usuarios del Sistema

| Usuario | Password | Rol | Email |
|---------|----------|-----|-------|
| admin | admin | ADMIN | admin@em.codelco.cl |
| gestor | gestor | GESTOR_PROYECTOS | gestor@em.codelco.cl |
| jefe | jefe | JEFE_PROYECTO | jefe@em.codelco.cl |
| contratista | contratista | CONTRATISTA | contratista@perforaciones.cl |

## Datos Incluidos

Después de ejecutar los 3 scripts:

| Tabla | Registros |
|-------|-----------|
| empresas | 5 |
| usuarios | 4 |
| proyectos | 4 |
| servicios | 7 |
| contratos | 9 |
| cargos | 60 |
| trabajadores | 225 |
| ciclos | 29 |
| asignaciones | 325 |
| requerimientos | 127 |

## Regenerar datos operativos

Si necesitas regenerar `003_data.sql` desde la base de datos actual:

```bash
python -m app.db.generate_sql
```

Esto sobrescribirá `sql/003_data.sql` con los datos actuales de la DB.

## Notas

- Los scripts usan IDs explícitos para garantizar consistencia
- Las secuencias se resetean automáticamente al final de cada script
- Ejecutar siempre en orden: 001 → 002 → 003
