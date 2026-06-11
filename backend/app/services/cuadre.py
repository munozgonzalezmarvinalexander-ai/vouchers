"""
services/cuadre.py
------------------
Las reglas contables de cuadre. Son funciones PURAS: no tocan la base de
datos, así que se prueban en milisegundos y se pueden reutilizar en cualquier
parte (al crear, al editar, al cambiar de estado).

Regla de oro: el dinero se maneja con Decimal, NUNCA con float. Con float,
652.00 + 603.02 puede dar 1255.0199999998 y un voucher "cuadrado" se vería
descuadrado por un centavo fantasma.
"""

from decimal import Decimal

CERO = Decimal("0")


def _monto(valor) -> Decimal:
    return valor if valor is not None else CERO


def validar_lineas(detalles) -> list[str]:
    """Cada línea debe llevar un monto al debe O al haber, no ambos ni ninguno.

    Devuelve la lista de errores (vacía si todo está bien).
    """
    errores: list[str] = []
    for i, d in enumerate(detalles, start=1):
        debe, haber = _monto(d.debe), _monto(d.haber)
        if debe < 0 or haber < 0:
            errores.append(f"Línea {i}: los montos no pueden ser negativos.")
        elif debe > 0 and haber > 0:
            errores.append(f"Línea {i}: una línea no puede llevar debe y haber a la vez.")
        elif debe == 0 and haber == 0:
            errores.append(f"Línea {i}: la línea debe llevar un monto en debe o en haber.")
    return errores


def calcular_totales(detalles) -> tuple[Decimal, Decimal, Decimal]:
    """Devuelve (total_debe, total_haber, diferencia)."""
    total_debe = sum((_monto(d.debe) for d in detalles), CERO)
    total_haber = sum((_monto(d.haber) for d in detalles), CERO)
    return total_debe, total_haber, total_debe - total_haber


def esta_cuadrado(detalles) -> bool:
    """True si el total del debe es exactamente igual al total del haber."""
    _, _, diferencia = calcular_totales(detalles)
    return diferencia == CERO
