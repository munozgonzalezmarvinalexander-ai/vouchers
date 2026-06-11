"""Pruebas de los documentos del voucher: HTML imprimible, PDF y Excel."""


def _crear_voucher(client):
    cuentas = {c["codigo"]: c["id"] for c in client.get("/cuentas").json()}
    pid = client.get("/proyectos").json()[0]["id"]
    r = client.post("/vouchers", json={
        "proyecto_id": pid, "fecha": "2026-06-08", "concepto": "Pago de combustible y dietas",
        "estado": "REVISADO",
        "detalles": [
            {"cuenta_id": cuentas["61201038"], "debe": "500.00"},
            {"cuenta_id": cuentas["61201295"], "debe": "750.00"},
            {"cuenta_id": cuentas["11102010"], "haber": "1250.00"},
        ],
    })
    assert r.status_code == 201, r.text
    return r.json()


def test_html_imprimible(client):
    v = _crear_voucher(client)
    r = client.get(f"/vouchers/{v['id']}/html?imprimir=1")
    assert r.status_code == 200
    assert "text/html" in r.headers["content-type"]
    # El número y un concepto deben aparecer; con imprimir=1 incluye window.print().
    assert v["numero"] in r.text
    assert "window.print()" in r.text


def test_excel(client):
    v = _crear_voucher(client)
    r = client.get(f"/vouchers/{v['id']}/excel")
    assert r.status_code == 200
    assert "spreadsheetml" in r.headers["content-type"]
    # Un .xlsx es un zip: empieza con la firma 'PK'.
    assert r.content[:2] == b"PK"


def test_pdf_responde(client):
    v = _crear_voucher(client)
    r = client.get(f"/vouchers/{v['id']}/pdf")
    # 200 si WeasyPrint está disponible; 503 (con aviso) si no. Nunca 404/500.
    assert r.status_code in (200, 503)
    if r.status_code == 200:
        assert r.content[:4] == b"%PDF"
