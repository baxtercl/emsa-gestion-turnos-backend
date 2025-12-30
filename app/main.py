"""
EMSA Gestion de Turnos - API Backend
Entry point de la aplicacion FastAPI
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.routers import (auth, ciclos, empresas, proyectos, servicios,
                         trabajadores, usuarios)

settings = get_settings()

# Crear aplicacion FastAPI
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="API REST para gestion de turnos y dotacion de operaciones mineras",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Endpoint raiz"""
    return {
        "app": settings.app_name,
        "version": settings.app_version,
        "status": "running",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


# Registrar routers
app.include_router(auth.router, prefix=f"{settings.api_v1_prefix}/auth", tags=["auth"])
app.include_router(
    empresas.router, prefix=f"{settings.api_v1_prefix}/empresas", tags=["empresas"]
)
app.include_router(
    servicios.router, prefix=f"{settings.api_v1_prefix}/servicios", tags=["servicios"]
)
app.include_router(
    proyectos.router, prefix=f"{settings.api_v1_prefix}/proyectos", tags=["proyectos"]
)
app.include_router(
    ciclos.router, prefix=f"{settings.api_v1_prefix}/ciclos", tags=["ciclos"]
)
app.include_router(
    usuarios.router, prefix=f"{settings.api_v1_prefix}/usuarios", tags=["usuarios"]
)
app.include_router(
    trabajadores.router,
    prefix=f"{settings.api_v1_prefix}/trabajadores",
    tags=["trabajadores"],
)
