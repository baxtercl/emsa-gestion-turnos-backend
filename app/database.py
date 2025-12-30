"""
Configuracion de conexion a PostgreSQL
Soporta conexion local y Cloud SQL via Unix socket
"""

import os

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.config import get_settings

settings = get_settings()


def get_database_url() -> str:
    """
    Construye la URL de conexion a la base de datos.

    En Cloud Run: usa Unix socket via Cloud SQL Proxy
    En local: usa conexion TCP directa

    Formatos soportados:
    - Cloud SQL: postgresql://user:pass@/dbname?host=/cloudsql/project:region:instance
    - Local: postgresql://user:pass@localhost:5432/dbname
    """
    # Si DATABASE_URL ya tiene formato de Cloud SQL (con ?host=), usarla directamente
    if settings.database_url and "?host=" in settings.database_url:
        return settings.database_url

    # Si hay INSTANCE_CONNECTION_NAME, construir URL para Cloud SQL
    instance_connection_name = os.getenv("INSTANCE_CONNECTION_NAME")
    if instance_connection_name:
        # Extraer credenciales de DATABASE_URL si existe
        # Formato esperado: postgresql://user:pass@/dbname
        db_url = settings.database_url
        if db_url:
            # Agregar el socket path si no está presente
            if "?" not in db_url:
                return f"{db_url}?host=/cloudsql/{instance_connection_name}"

        # Construir desde variables individuales si DATABASE_URL no tiene el formato correcto
        db_user = os.getenv("DB_USER", "app_user")
        db_pass = os.getenv("DB_PASSWORD", "")
        db_name = os.getenv("DB_NAME", "emsa_gestion_turnos")
        return f"postgresql://{db_user}:{db_pass}@/{db_name}?host=/cloudsql/{instance_connection_name}"

    # Desarrollo local: usar DATABASE_URL tal cual
    return settings.database_url


# Obtener URL de base de datos
database_url = get_database_url()

# Engine de SQLAlchemy
engine = create_engine(
    database_url,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
)

# Sesion de base de datos
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para modelos
Base = declarative_base()


def get_db():
    """
    Dependency para obtener sesion de base de datos.
    Se usa en los endpoints con Depends(get_db).
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
