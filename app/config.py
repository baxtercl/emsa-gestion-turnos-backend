"""
Configuracion de la aplicacion
"""

from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Configuracion cargada desde variables de entorno"""

    # Aplicacion
    app_name: str = "EMSA Gestion de Turnos"
    app_version: str = "1.0.0"
    debug: bool = False
    environment: str = "development"

    # Base de Datos
    database_url: str = "postgresql://postgres:password@localhost:5432/emsa_turnos"

    # JWT
    secret_key: str = "your-super-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    # CORS
    cors_origins: str = "http://localhost:5173,http://localhost:3000"

    # API
    api_v1_prefix: str = "/api/v1"

    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"  # Ignorar variables de entorno no definidas

    @property
    def cors_origins_list(self) -> list[str]:
        """Retorna lista de origenes CORS"""
        return [origin.strip() for origin in self.cors_origins.split(",")]


@lru_cache()
def get_settings() -> Settings:
    """Singleton de configuracion"""
    return Settings()
