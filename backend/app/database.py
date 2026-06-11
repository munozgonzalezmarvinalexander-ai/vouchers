"""
database.py
-----------
Crea la conexión a la base de datos (el "engine"), la fábrica de sesiones
y la clase Base de la que heredan todos los modelos.

Funciona igual con SQLite o con Postgres: lo único que cambia es la URL.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.config import settings


class Base(DeclarativeBase):
    """Clase base de todos los modelos (tablas). SQLAlchemy 2.0."""
    pass


# SQLite necesita este argumento para usarse desde varios hilos.
# Postgres no lo necesita, así que solo se agrega cuando la URL es SQLite.
_connect_args = (
    {"check_same_thread": False}
    if settings.database_url.startswith("sqlite")
    else {}
)

engine = create_engine(
    settings.database_url,
    echo=False,            # ponlo en True si quieres ver el SQL que se ejecuta
    pool_pre_ping=True,    # importante para Neon: revive conexiones inactivas
    connect_args=_connect_args,
)

# Cada sesión es una "conversación" con la base de datos.
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def get_db():
    """Entrega una sesión y se asegura de cerrarla al terminar.

    (En la Etapa 2, FastAPI usará esto como dependencia en cada endpoint.)
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
