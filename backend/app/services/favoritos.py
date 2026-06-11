"""
services/favoritos.py
---------------------
Favoritos AUTOMÁTICOS. No se configuran a mano: son las cuentas más usadas en
los vouchers de cada proyecto. La "verdad" es el historial mismo, así que la
lista se alimenta sola conforme creas vouchers:

  - Sistema recién instalado, sin vouchers -> lista vacía.
  - Cada voucher que creas suma uso a sus cuentas.
  - Las N más usadas (por defecto 15) suben solas a "favoritas".

Los vouchers ANULADOS no cuentan.
"""

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models import Cuenta, Voucher, VoucherDetalle


def cuentas_frecuentes(db: Session, proyecto_id: int, limite: int = 15):
    """Devuelve [(Cuenta, usos), ...] ordenado de más a menos usado."""
    usos = func.count(VoucherDetalle.id)
    filas = (
        db.query(Cuenta, usos.label("usos"))
        .join(VoucherDetalle, VoucherDetalle.cuenta_id == Cuenta.id)
        .join(Voucher, Voucher.id == VoucherDetalle.voucher_id)
        .filter(Voucher.proyecto_id == proyecto_id, Voucher.estado != "ANULADO")
        .group_by(Cuenta.id)
        .order_by(usos.desc(), Cuenta.codigo)
        .limit(limite)
        .all()
    )
    return filas
