# Sistema de Gestión de Turnos HSEC - Backend

## Perfil del Asistente

Eres un desarrollador de software experimentado con amplia experiencia en:
- **Backend**: Python, FastAPI, SQLAlchemy, PostgreSQL, Alembic
- **Seguridad**: JWT, OAuth2, RBAC, bcrypt
- **Buenas prácticas**: Clean Code, SOLID, testing, code review

Aplicas patrones de diseño apropiados y escribes código mantenible, escalable y bien documentado.

## Descripción del Proyecto

API REST para el sistema de gestión integral de turnos y dotación para operaciones mineras:
- Gestión de ciclos de turnos (A/B/C/D) con patrones variables (4x3, 5x2, 7x7, 10x10, 14x14)
- Control de cobertura de dotación
- Monitoreo de estándares operacionales HSEC
- Visibilidad para mandantes (fiscalizadores) y contratistas

## Stack Tecnológico

- **Framework**: FastAPI 0.109+
- **ORM**: SQLAlchemy 2.0+
- **Migraciones**: Alembic 1.13+
- **Base de Datos**: PostgreSQL 17 (Cloud SQL)
- **Cloud**: Google Cloud Platform (Cloud Run + Cloud SQL)
- **Autenticación**: JWT (python-jose) + bcrypt (passlib)
- **Validación**: Pydantic 2.5+
- **Servidor ASGI**: Uvicorn
- **Testing**: pytest, pytest-asyncio

## Estructura del Proyecto

```
app/
├── main.py           # Punto de entrada FastAPI
├── config.py         # Configuración centralizada
├── database.py       # Conexión y sesión de BD
├── models/           # Modelos SQLAlchemy
│   ├── empresa.py
│   ├── usuario.py
│   ├── proyecto.py
│   ├── servicio.py
│   ├── contrato.py
│   ├── cargo.py
│   ├── trabajador.py
│   ├── ciclo.py
│   └── asignacion.py
├── schemas/          # Schemas Pydantic (request/response)
│   ├── auth.py
│   ├── empresa.py
│   ├── proyecto.py
│   ├── contrato.py
│   ├── ciclo.py
│   └── ...
├── routers/          # Endpoints API
│   ├── auth.py
│   ├── empresas.py
│   ├── proyectos.py
│   ├── ciclos.py
│   └── ...
├── db/               # Scripts de base de datos
│   ├── schema.sql    # Schema completo de BD
│   └── seed.sql      # Datos de prueba
├── services/         # Lógica de negocio
└── utils/
    ├── security.py   # JWT y hashing
    └── permissions.py # Sistema RBAC
sql/                  # (legacy, usar app/db/)
├── 001_schema.sql
└── 002_seed.sql
```

## Convenciones de Código

### Nombrado
- **Modelos**: PascalCase singular (ej: `Proyecto`, `Trabajador`)
- **Schemas**: PascalCase con sufijo (ej: `ProyectoCreate`, `ProyectoResponse`)
- **Routers**: snake_case plural (ej: `proyectos.py`, `ciclos.py`)
- **Funciones**: snake_case (ej: `get_proyecto_by_id`)
- **Constantes**: SCREAMING_SNAKE_CASE (ej: `API_V1_PREFIX`)

### Idioma
- **UI/Mensajes**: Español (mensajes de error, descripciones)
- **Código**: Inglés (variables, funciones, comentarios técnicos)
- **Entidades BD**: Español (nombres de tablas y columnas)

### Commits
- Sin firma de autor (sin Co-Authored-By)
- Mensajes en español
- Formato: `tipo: descripción breve`

## Entidades Principales

| Entidad | Tabla | Descripción |
|---------|-------|-------------|
| Empresa | `empresas` | Mandante (EMSA) o contratistas |
| Usuario | `usuarios` | Usuarios del sistema con roles |
| Proyecto | `proyectos` | Contenedor principal de operación |
| Servicio | `servicios` | Tipos de servicio (perforación, etc.) |
| Contrato | `contratos` | Reglas de turno por empresa/servicio |
| Cargo | `cargos` | Posiciones jerárquicas |
| Trabajador | `trabajadores` | Personal con RUT chileno validado |
| Ciclo | `ciclos` | Período de turno (A/B/C/D) |
| Asignacion | `asignaciones` | Trabajador asignado a ciclo |
| Requerimiento | `requerimientos` | Cantidad necesaria por cargo/ciclo |

## Roles de Usuario (RBAC)

| Rol | Código | Permisos |
|-----|--------|----------|
| Admin | `ADMIN` | Control total del sistema |
| Gestor de Proyectos | `GESTOR_PROYECTOS` | CRUD de todos los proyectos |
| Jefe de Proyecto | `JEFE_PROYECTO` | Gestiona solo su(s) proyecto(s) |
| Contratista | `CONTRATISTA` | Solo lectura de su empresa |

### Usuarios de Prueba

| Rol | Email | Password |
|-----|-------|----------|
| Admin | admin@em.codelco.cl | admin |
| Gestor | gestor@em.codelco.cl | gestor |
| Jefe Proyecto | jefe@em.codelco.cl | jefe |
| Contratista | contratista@perforaciones.cl | contratista |

## API Endpoints

### Autenticación
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | `/api/v1/auth/login` | Iniciar sesión |
| GET | `/api/v1/auth/me` | Usuario actual |
| POST | `/api/v1/auth/logout` | Cerrar sesión |

### Proyectos
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/v1/proyectos` | Lista de proyectos |
| GET | `/api/v1/proyectos/{id}` | Detalle de proyecto |
| GET | `/api/v1/proyectos/{id}/panel-mandante` | Panel resumen |
| GET | `/api/v1/proyectos/{id}/contratos` | Contratos del proyecto |
| GET | `/api/v1/proyectos/{id}/cargos` | Cargos del proyecto |
| GET | `/api/v1/proyectos/{id}/cargos/tree` | Organigrama árbol |
| GET | `/api/v1/proyectos/{id}/trabajadores` | Trabajadores |
| GET | `/api/v1/proyectos/{id}/ciclos` | Ciclos del proyecto |
| GET | `/api/v1/proyectos/{id}/ciclos/calendario` | Calendario |

### Ciclos
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/v1/ciclos/{id}/requerimientos` | Requerimientos |
| GET | `/api/v1/ciclos/{id}/asignaciones` | Asignaciones |

### Maestros
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/v1/empresas` | Lista de empresas |
| GET | `/api/v1/servicios` | Lista de servicios |

## Rutas del Proyecto

| Componente | Ruta |
|------------|------|
| **Backend** | `C:\Users\Asaav031\OneDrive - Codelco\Projects\emsa-gestion-turnos\emsa-gestion-turnos-backend\` |
| **Frontend** | `C:\Users\Asaav031\OneDrive - Codelco\Projects\emsa-gestion-turnos\emsa-gestion-turnos-frontend\` |
| **Documentación** | `C:\Users\Asaav031\OneDrive - Codelco\Projects\sistema_turnos\docs\` |

## Entorno de Desarrollo

- **Entorno virtual**: `emsa-backend`
- **Python**: 3.12

```bash
# Activar entorno virtual (Windows)
conda activate emsa-backend

# Verificar versión de Python
python --version  # Python 3.12.x
```

## Comandos Útiles

```bash
# Instalar dependencias
pip install -r requirements.txt

# Desarrollo (con auto-reload)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Producción
uvicorn app.main:app --host 0.0.0.0 --port 8000

# Tests
pytest

# Formatear código
black app/
isort app/

# Lint
flake8 app/
```

## Calidad de Código

### Verificación Obligatoria

Antes de considerar cualquier tarea completada, **SIEMPRE** ejecutar:

1. **Black** - Formatear el código:
   ```bash
   black app/
   ```

2. **isort** - Ordenar imports:
   ```bash
   isort app/
   ```

3. **Flake8** - Verificar linting:
   ```bash
   flake8 app/
   ```

4. **Tests** - Ejecutar tests:
   ```bash
   pytest
   ```

### Reglas

- No dejar warnings de flake8 sin resolver
- Todo el código debe estar formateado con Black
- Imports organizados con isort
- Resolver errores de tipo de Pydantic inmediatamente

## Variables de Entorno

```bash
# Aplicacion
APP_NAME=EMSA Gestion de Turnos
APP_VERSION=1.0.0
DEBUG=True
ENVIRONMENT=development

# Base de datos (desarrollo local con Cloud SQL Proxy)
DATABASE_URL=postgresql://app_user:TU_PASSWORD@localhost:5432/emsa_gestion_turnos

# Base de datos (Cloud Run - produccion)
# DATABASE_URL=postgresql://app_user:TU_PASSWORD@/emsa_gestion_turnos?host=/cloudsql/emsa-gestion-turnos:southamerica-east1:emsa-gestion-turnos-db

# JWT
SECRET_KEY=your-super-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS
CORS_ORIGINS=http://localhost:5173,http://localhost:3000

# API
API_V1_PREFIX=/api/v1
```

## Base de Datos (Cloud SQL)

- **Motor**: PostgreSQL 17 (Cloud SQL)
- **Instancia**: `emsa-gestion-turnos-db`
- **Region**: `southamerica-east1`
- **Connection Name**: `emsa-gestion-turnos:southamerica-east1:emsa-gestion-turnos-db`
- **ORM**: SQLAlchemy 2.0
- **Vistas**: `v_cobertura_ciclos`, `v_dotacion_proyecto`

### Setup Local (con Cloud SQL Proxy)

```bash
# 1. Descargar Cloud SQL Proxy
curl -o cloud-sql-proxy.exe https://storage.googleapis.com/cloud-sql-connectors/cloud-sql-proxy/v2.14.0/cloud-sql-proxy.x64.exe

# 2. Autenticarse
gcloud auth application-default login

# 3. Ejecutar proxy (en terminal separada)
.\cloud-sql-proxy.exe emsa-gestion-turnos:southamerica-east1:emsa-gestion-turnos-db --port=5432

# 4. Ejecutar schema
psql -h localhost -U app_user -d emsa_gestion_turnos -f app/db/schema.sql

# 5. Cargar datos de prueba
psql -h localhost -U app_user -d emsa_gestion_turnos -f app/db/seed.sql
```

### Recursos Cloud SQL

| Recurso | Valor |
|---------|-------|
| Instancia | `emsa-gestion-turnos-db` |
| Version | PostgreSQL 17 |
| Region | `southamerica-east1` |
| Tier | `db-f1-micro` |
| Base de datos | `emsa_gestion_turnos` |
| Usuario | `app_user` |

## Patrones de Turnos

| Patrón | Días Trabajo | Días Descanso |
|--------|--------------|---------------|
| 4x3 | 4 | 3 |
| 5x2 | 5 | 2 |
| 7x7 | 7 | 7 |
| 8x6 | 8 | 6 |
| 10x10 | 10 | 10 |
| 14x14 | 14 | 14 |

## Tipos de Turno

| Tipo | Letras | Descripción |
|------|--------|-------------|
| AB | A, B | 2 turnos alternados |
| ABCD | A, B, C, D | 4 turnos rotativos |

## Colores de Turno

- **Turno A**: Azul (`#4a7bc1`)
- **Turno B**: Verde (`#5fad43`)
- **Turno C**: Naranja (`#f5a02b`)
- **Turno D**: Rojo (`#f13a5c`)
