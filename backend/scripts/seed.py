"""
seed.py
-------
Crea las tablas en la base de datos (la que indique DATABASE_URL) y carga el
catálogo limpio desde los CSV de la carpeta data/.

Es IDEMPOTENTE: puedes ejecutarlo las veces que quieras. Si una cuenta o
proyecto ya existe, lo actualiza; no crea duplicados.

Uso (desde la raíz del proyecto):
    python scripts/seed.py
"""

import csv
import sys
from pathlib import Path

# Permite ejecutar el script directamente: agrega la raíz del proyecto al path
# para poder importar el paquete 'app'.
RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from app.database import Base, SessionLocal, engine  # noqa: E402
from app.models import Cuenta, Firmante, Proyecto  # noqa: E402

DATA = RAIZ / "data"

# Firmantes por defecto (tomados del voucher real).
FIRMANTES = [
    {"nombre": "Carina López", "cargo": "Contabilidad", "rol_firma": "ELABORA"},
    {"nombre": "Haroldo Oquendo", "cargo": "Revisión", "rol_firma": "REVISA"},
    {"nombre": "Miguel López", "cargo": "Dirección", "rol_firma": "AUTORIZA"},
]


def leer_csv(nombre: str) -> list[dict]:
    with (DATA / nombre).open(encoding="utf-8") as f:
        return list(csv.DictReader(f))


def sembrar_cuentas(db) -> int:
    for fila in leer_csv("catalogo_cuentas.csv"):
        cuenta = db.query(Cuenta).filter_by(codigo=fila["codigo"]).one_or_none()
        if cuenta is None:
            cuenta = Cuenta(codigo=fila["codigo"])
            db.add(cuenta)
        # Crear o actualizar campos (idempotente).
        cuenta.nombre = fila["nombre"]
        cuenta.tipo = fila["tipo"]
        cuenta.naturaleza = fila["naturaleza"]
        cuenta.es_banco = fila["es_banco"] == "1"
        cuenta.numero_cuenta = fila["numero_cuenta"] or None
        cuenta.resultado = fila["resultado"] or None
        cuenta.activo = fila["activo"] == "1"
    db.commit()
    return db.query(Cuenta).count()


def sembrar_proyectos(db) -> int:
    for fila in leer_csv("proyectos.csv"):
        proyecto = db.query(Proyecto).filter_by(codigo=fila["codigo"]).one_or_none()
        if proyecto is None:
            proyecto = Proyecto(codigo=fila["codigo"])
            db.add(proyecto)
        proyecto.nombre = fila["nombre"]
        proyecto.donante = fila["donante"] or None
        proyecto.activo = fila["activo"] == "1"
    db.commit()
    return db.query(Proyecto).count()


def sembrar_firmantes(db) -> int:
    for f in FIRMANTES:
        existe = (
            db.query(Firmante)
            .filter_by(nombre=f["nombre"], rol_firma=f["rol_firma"])
            .one_or_none()
        )
        if existe is None:
            db.add(Firmante(**f))
    db.commit()
    return db.query(Firmante).count()


def main():
    print(f"Base de datos: {engine.url}")
    print("Creando tablas (si no existen)...")
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        n_cuentas = sembrar_cuentas(db)
        n_proyectos = sembrar_proyectos(db)
        n_firmantes = sembrar_firmantes(db)
    finally:
        db.close()

    print("Carga completa:")
    print(f"  Cuentas   : {n_cuentas}")
    print(f"  Proyectos : {n_proyectos}")
    print(f"  Firmantes : {n_firmantes}")
    print("  (Los favoritos se calculan por uso; no se siembran.)")


if __name__ == "__main__":
    main()
