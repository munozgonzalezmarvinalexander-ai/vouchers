"""
config.py
---------
Centraliza la configuración. La única pieza que importa por ahora es la
conexión a la base de datos, que se lee de la variable de entorno DATABASE_URL.

- Si NO defines DATABASE_URL, la app usa un archivo SQLite local (cero
  configuración, ideal para probar en cualquier computadora).
- Si defines DATABASE_URL (por ejemplo, la de Neon), la MISMA app usa ese
  Postgres compartido. No cambia ninguna otra línea del proyecto.
"""

import os
from dotenv import load_dotenv

# Carga las variables del archivo .env (si existe) al entorno.
load_dotenv()


def _normalizar_url(url: str) -> str:
    """Asegura que la URL de Postgres use el driver psycopg2.

    Muchos proveedores entregan la URL como 'postgres://...' o
    'postgresql://...'. SQLAlchemy necesita saber el driver, así que la
    convertimos a 'postgresql+psycopg2://...'.
    """
    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql+psycopg2://", 1)
    if url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+psycopg2://", 1)
    return url


class Settings:
    # Valor por defecto: SQLite en un archivo local llamado vouchers.db
    database_url: str = _normalizar_url(
        os.getenv("DATABASE_URL", "sqlite:///./vouchers.db")
    )


settings = Settings()
