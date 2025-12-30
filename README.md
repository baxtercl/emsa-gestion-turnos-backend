# EMSA Gestion de Turnos - Backend

API REST para el sistema de gestion de turnos y dotacion de operaciones mineras.

## Stack Tecnologico

- **Framework**: FastAPI 0.109+
- **Base de Datos**: PostgreSQL 14+
- **ORM**: SQLAlchemy 2.0
- **Migraciones**: Alembic
- **Autenticacion**: JWT (python-jose)
- **Validacion**: Pydantic 2.x

## Estructura del Proyecto

```
emsa-gestion-turnos-backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # Entry point FastAPI
│   ├── config.py            # Configuracion
│   ├── database.py          # Conexion PostgreSQL
│   ├── models/              # Modelos SQLAlchemy
│   │   ├── __init__.py
│   │   ├── empresa.py
│   │   ├── usuario.py
│   │   ├── proyecto.py
│   │   ├── servicio.py
│   │   ├── contrato.py
│   │   ├── cargo.py
│   │   ├── trabajador.py
│   │   ├── ciclo.py
│   │   └── asignacion.py
│   ├── schemas/             # Pydantic schemas
│   │   └── ...
│   ├── routers/             # Endpoints API
│   │   ├── auth.py
│   │   ├── usuarios.py
│   │   ├── proyectos.py
│   │   └── ...
│   ├── services/            # Logica de negocio
│   │   └── ...
│   └── utils/               # Utilidades
│       ├── security.py      # JWT, hashing
│       └── permissions.py   # RBAC
├── sql/
│   ├── 001_schema.sql       # Estructura de tablas
│   └── 002_seed.sql         # Datos iniciales
├── tests/
│   └── ...
├── .env.example
├── requirements.txt
└── README.md
```

## Instalacion

### 1. Crear entorno virtual

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 2. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 3. Configurar variables de entorno

```bash
cp .env.example .env
# Editar .env con las credenciales reales
```

### 4. Crear base de datos

```bash
# Conectar a PostgreSQL y ejecutar:
createdb emsa_turnos

# Ejecutar scripts SQL
psql -d emsa_turnos -f sql/001_schema.sql
psql -d emsa_turnos -f sql/002_seed.sql
```

### 5. Ejecutar servidor

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Documentacion API

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Usuarios de Prueba

| Rol | Email | Password |
|-----|-------|----------|
| ADMIN | admin@emsa.cl | admin |
| GESTOR_PROYECTOS | gestor@emsa.cl | gestor |
| JEFE_PROYECTO | jefe@emsa.cl | jefe |
| CONTRATISTA | contratista@perforaciones.cl | contratista |

## Roles y Permisos

| Rol | Descripcion | Alcance |
|-----|-------------|---------|
| ADMIN | Superusuario | Control total del sistema |
| GESTOR_PROYECTOS | Gestor | Todos los proyectos |
| JEFE_PROYECTO | Jefe | Solo proyectos asignados |
| CONTRATISTA | EECC | Solo datos de su empresa |

## Comandos Utiles

```bash
# Desarrollo
uvicorn app.main:app --reload

# Testing
pytest

# Formateo
black app/
isort app/

# Lint
flake8 app/
```

## Variables de Entorno

| Variable | Descripcion | Ejemplo |
|----------|-------------|---------|
| DATABASE_URL | URL PostgreSQL | postgresql://user:pass@localhost/db |
| SECRET_KEY | Clave JWT | your-secret-key |
| CORS_ORIGINS | Origenes permitidos | http://localhost:5173 |

## Licencia

Proyecto interno EMSA - Todos los derechos reservados
