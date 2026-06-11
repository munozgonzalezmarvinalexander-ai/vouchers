"""
tests/conftest.py
-----------------
Configuración compartida de las pruebas. Crea una base SQLite EN MEMORIA
(rápida y desechable), la siembra con datos mínimos y entrega:
  - `db`     : una sesión a esa base
  - `client` : un cliente HTTP que apunta a la API usando esa misma base
"""

import os

# La app crea sus tablas al arrancar; usamos SQLite en memoria para no tocar
# ningún archivo durante las pruebas.
os.environ.setdefault("DATABASE_URL", "sqlite://")

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app import models
from app.database import Base, get_db
from app.main import app


@pytest.fixture()
def db():
    # StaticPool mantiene UNA sola conexión: necesario para que la base en
    # memoria persista entre llamadas dentro de la misma prueba.
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    sesion = Session()

    # Datos mínimos: un proyecto, dos partidas de gasto y un banco.
    sesion.add_all([
        models.Proyecto(codigo="knh-salud", nombre="KNH Salud"),
        models.Cuenta(codigo="61201038", nombre="COMBUSTIBLE", tipo="GASTO", naturaleza="DEUDORA"),
        models.Cuenta(codigo="61201295", nombre="DIETAS", tipo="GASTO", naturaleza="DEUDORA"),
        models.Cuenta(codigo="11102010", nombre="BANCO INDUSTRIAL, S.A.", tipo="BANCO",
                      naturaleza="DEUDORA", es_banco=True, numero_cuenta="002-005041-9"),
    ])
    sesion.commit()

    yield sesion
    sesion.close()


@pytest.fixture()
def client(db):
    # Hacemos que la API use la sesión de prueba en lugar de la real.
    app.dependency_overrides[get_db] = lambda: db
    yield TestClient(app)
    app.dependency_overrides.clear()
