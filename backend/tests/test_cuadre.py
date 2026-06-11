"""Pruebas de las reglas de cuadre (funciones puras, sin base de datos)."""

from decimal import Decimal
from types import SimpleNamespace

from app.services.cuadre import calcular_totales, esta_cuadrado, validar_lineas


def linea(debe=0, haber=0):
    """Crea un objeto sencillo con .debe y .haber, como una línea de voucher."""
    return SimpleNamespace(debe=Decimal(str(debe)), haber=Decimal(str(haber)))


def test_voucher_cuadrado():
    detalles = [linea(debe=500), linea(debe=750), linea(haber=1250)]
    total_debe, total_haber, diferencia = calcular_totales(detalles)
    assert total_debe == Decimal("1250")
    assert total_haber == Decimal("1250")
    assert diferencia == Decimal("0")
    assert esta_cuadrado(detalles)


def test_voucher_descuadrado():
    assert not esta_cuadrado([linea(debe=500), linea(haber=400)])


def test_linea_con_debe_y_haber_es_invalida():
    assert validar_lineas([linea(debe=100, haber=50)])


def test_linea_vacia_es_invalida():
    assert validar_lineas([linea()])


def test_lineas_validas_no_dan_errores():
    assert validar_lineas([linea(debe=500), linea(haber=500)]) == []


def test_centavos_exactos_con_decimal():
    # 652.00 + 603.02 = 1255.02 exacto, sin el "centavo fantasma" del float.
    detalles = [linea(debe="652.00"), linea(debe="603.02"), linea(haber="1255.02")]
    assert esta_cuadrado(detalles)
