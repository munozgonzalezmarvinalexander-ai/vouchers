"""Pruebas de la Etapa 5: ortografía, reportes y auditoría."""

from decimal import Decimal


def _crear(client, combustible="500.00", dietas="750.00", estado="REVISADO"):
    cuentas = {c["codigo"]: c["id"] for c in client.get("/cuentas").json()}
    pid = client.get("/proyectos").json()[0]["id"]
    total = float(combustible) + float(dietas)
    r = client.post("/vouchers", json={
        "proyecto_id": pid, "fecha": "2026-06-08", "concepto": "Pago", "estado": estado,
        "detalles": [
            {"cuenta_id": cuentas["61201038"], "debe": combustible},
            {"cuenta_id": cuentas["61201295"], "debe": dietas},
            {"cuenta_id": cuentas["11102010"], "haber": f"{total:.2f}"},
        ],
    })
    assert r.status_code == 201, r.text
    return r.json()


# --- Ortografía ---
def test_ortografia_detecta_error_y_respeta_dominio(client):
    r = client.post("/ortografia/revisar", json={"texto": "Pago a CONACMI por consultoria"})
    assert r.status_code == 200
    palabras = [p["palabra"].lower() for p in r.json()["palabras"]]
    assert "consultoria" in palabras       # falta la tilde -> se marca
    assert "conacmi" not in palabras        # término del dominio -> NO se marca


# --- Reportes ---
def test_libro_vouchers(client):
    _crear(client)
    _crear(client)
    data = client.get("/reportes/libro-vouchers").json()
    assert data["conteo"] == 2
    assert Decimal(str(data["total"])) == Decimal("2500.00")


def test_totales_por_partida(client):
    _crear(client)
    filas = client.get("/reportes/totales-por-partida").json()
    porcod = {f["codigo"]: f for f in filas}
    assert Decimal(str(porcod["61201038"]["total"])) == Decimal("500.00")
    assert Decimal(str(porcod["61201295"]["total"])) == Decimal("750.00")
    # El banco va al haber, no al debe: no aparece en gastos por partida.
    assert "11102010" not in porcod


def test_libro_excel(client):
    _crear(client)
    r = client.get("/reportes/libro-vouchers/excel")
    assert r.status_code == 200
    assert r.content[:2] == b"PK"


# --- Auditoría ---
def test_auditoria_registra_acciones(client):
    v = _crear(client, estado="BORRADOR")
    acciones = [a["accion"] for a in client.get(f"/vouchers/{v['id']}/auditoria").json()]
    assert "CREADO" in acciones
    client.patch(f"/vouchers/{v['id']}/estado", json={"estado": "REVISADO"})
    acciones = [a["accion"] for a in client.get(f"/vouchers/{v['id']}/auditoria").json()]
    assert "REVISADO" in acciones and "CREADO" in acciones
