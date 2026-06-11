"""Pruebas de numeración correlativa y de los endpoints de vouchers."""

from decimal import Decimal

from app.models import Proyecto
from app.services.numeracion import siguiente_numero


def test_numeracion_inicia_en_uno_por_proyecto_y_anio(db):
    proyecto = db.query(Proyecto).first()
    numero = siguiente_numero(db, proyecto, 2026)
    assert numero == "KNH-SALUD-2026-0001"


def _ids(client):
    cuentas = {c["codigo"]: c["id"] for c in client.get("/cuentas").json()}
    proyecto_id = client.get("/proyectos").json()[0]["id"]
    return proyecto_id, cuentas


def test_crear_voucher_cuadrado(client):
    proyecto_id, cuentas = _ids(client)
    payload = {
        "proyecto_id": proyecto_id,
        "fecha": "2026-06-08",
        "concepto": "Reintegro de combustible y dietas",
        "estado": "REVISADO",
        "detalles": [
            {"cuenta_id": cuentas["61201038"], "debe": "500.00"},
            {"cuenta_id": cuentas["61201295"], "debe": "750.00"},
            {"cuenta_id": cuentas["11102010"], "haber": "1250.00"},
        ],
    }
    r = client.post("/vouchers", json=payload)
    assert r.status_code == 201, r.text
    data = r.json()
    assert data["estado"] == "REVISADO"
    assert data["numero"] == "KNH-SALUD-2026-0001"
    assert Decimal(str(data["total_debe"])) == Decimal("1250.00")
    assert Decimal(str(data["total_haber"])) == Decimal("1250.00")
    # El banco se detecta solo (es la línea cuya cuenta es de banco).
    assert data["banco"]["numero_cuenta"] == "002-005041-9"
    # La descripción de una línea se autocompletó con el nombre de la cuenta.
    assert any(d["descripcion"] == "COMBUSTIBLE" for d in data["detalles"])


def test_rechaza_voucher_descuadrado(client):
    proyecto_id, cuentas = _ids(client)
    payload = {
        "proyecto_id": proyecto_id,
        "fecha": "2026-06-08",
        "concepto": "Voucher mal cuadrado",
        "estado": "REVISADO",
        "detalles": [
            {"cuenta_id": cuentas["61201038"], "debe": "500.00"},
            {"cuenta_id": cuentas["11102010"], "haber": "400.00"},
        ],
    }
    r = client.post("/vouchers", json=payload)
    assert r.status_code == 400
    assert "no cuadra" in r.json()["detail"].lower()


def test_borrador_puede_quedar_descuadrado(client):
    proyecto_id, cuentas = _ids(client)
    payload = {
        "proyecto_id": proyecto_id,
        "fecha": "2026-06-08",
        "concepto": "Trabajo en progreso",
        "estado": "BORRADOR",
        "detalles": [
            {"cuenta_id": cuentas["61201038"], "debe": "500.00"},
            {"cuenta_id": cuentas["11102010"], "haber": "400.00"},
        ],
    }
    # Un borrador SÍ puede guardarse descuadrado (aún se está armando).
    assert client.post("/vouchers", json=payload).status_code == 201


def test_flujo_de_estados(client):
    proyecto_id, cuentas = _ids(client)
    payload = {
        "proyecto_id": proyecto_id,
        "fecha": "2026-06-08",
        "concepto": "Para probar el flujo de estados",
        "detalles": [
            {"cuenta_id": cuentas["61201038"], "debe": "100.00"},
            {"cuenta_id": cuentas["11102010"], "haber": "100.00"},
        ],
    }
    vid = client.post("/vouchers", json=payload).json()["id"]
    # BORRADOR -> REVISADO (cuadra: permitido)
    assert client.patch(f"/vouchers/{vid}/estado", json={"estado": "REVISADO"}).status_code == 200
    # REVISADO -> AUTORIZADO
    assert client.patch(f"/vouchers/{vid}/estado", json={"estado": "AUTORIZADO"}).status_code == 200
    # AUTORIZADO -> REVISADO (no permitido: un autorizado ya no retrocede)
    assert client.patch(f"/vouchers/{vid}/estado", json={"estado": "REVISADO"}).status_code == 400
