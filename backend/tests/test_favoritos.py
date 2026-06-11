"""Prueba de los favoritos AUTOMÁTICOS: empiezan vacíos y se ordenan por uso."""


def test_favoritas_se_alimentan_por_uso(client):
    cuentas = {c["codigo"]: c["id"] for c in client.get("/cuentas").json()}
    pid = client.get("/proyectos").json()[0]["id"]

    # Sistema recién sembrado, sin vouchers -> no hay favoritas todavía.
    assert client.get(f"/proyectos/{pid}/cuentas-frecuentes").json() == []

    def crear(combustible, dietas):
        detalles = [{"cuenta_id": cuentas["11102010"], "haber": str(combustible + dietas)}]
        if dietas:
            detalles.insert(0, {"cuenta_id": cuentas["61201295"], "debe": str(dietas)})
        if combustible:
            detalles.insert(0, {"cuenta_id": cuentas["61201038"], "debe": str(combustible)})
        r = client.post("/vouchers", json={
            "proyecto_id": pid, "fecha": "2026-06-08", "concepto": "uso",
            "estado": "REVISADO", "detalles": detalles,
        })
        assert r.status_code == 201, r.text

    crear(100, 50)   # usa combustible, dietas y banco
    crear(100, 0)    # usa combustible y banco

    favs = client.get(f"/proyectos/{pid}/cuentas-frecuentes").json()
    codigos = [f["codigo"] for f in favs]

    # Combustible se usó 2 veces; dietas 1 vez -> combustible va primero.
    assert codigos.index("61201038") < codigos.index("61201295")
    # La lista viene ordenada de más a menos usada.
    assert favs[0]["usos"] >= favs[-1]["usos"]
    # Y trae el conteo de usos de cada cuenta.
    usos = {f["codigo"]: f["usos"] for f in favs}
    assert usos["61201038"] == 2 and usos["61201295"] == 1
