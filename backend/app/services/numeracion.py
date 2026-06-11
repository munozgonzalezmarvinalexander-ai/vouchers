"""
services/numeracion.py
----------------------
Genera el número correlativo de cada voucher, por proyecto y por año.
Ejemplo: KNH-SALUD-2026-0001, KNH-SALUD-2026-0002, ...

Esto resuelve uno de los problemas del Excel: allí no había numeración formal,
el "control" era la posición en la hoja.
"""

import re

from app.models import Proyecto, Voucher


def _prefijo(proyecto: Proyecto) -> str:
    base = (proyecto.codigo or proyecto.nombre).upper().replace(" ", "-")
    base = re.sub(r"[^A-Z0-9-]", "", base)
    return base.strip("-") or "VCH"


def siguiente_numero(db, proyecto: Proyecto, anio: int) -> str:
    """Cuenta los vouchers ya emitidos para ese proyecto y año, y suma 1.

    Se cuenta por patrón de texto (LIKE) para no depender de funciones de fecha
    distintas entre SQLite y Postgres. Como los vouchers anulados conservan su
    número, los correlativos no se reutilizan.
    """
    prefijo = _prefijo(proyecto)
    patron = f"{prefijo}-{anio}-%"
    usados = (
        db.query(Voucher)
        .filter(Voucher.proyecto_id == proyecto.id, Voucher.numero.like(patron))
        .count()
    )
    return f"{prefijo}-{anio}-{usados + 1:04d}"
