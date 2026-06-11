"""
api/cuentas.py
--------------
Endpoints del catálogo de cuentas. Los routers solo reciben la petición,
llaman a la base de datos y devuelven el resultado; no contienen reglas de
negocio (esas viven en services/).
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Cuenta
from app.schemas import CuentaCreate, CuentaOut, CuentaUpdate

router = APIRouter(prefix="/cuentas", tags=["Catálogo de cuentas"])


@router.get("", response_model=list[CuentaOut])
def listar_cuentas(
    q: str | None = Query(None, description="Busca por código o nombre"),
    tipo: str | None = Query(None, description="GASTO | BANCO | ACTIVO | PASIVO"),
    es_banco: bool | None = None,
    activo: bool | None = True,
    db: Session = Depends(get_db),
):
    consulta = db.query(Cuenta)
    if activo is not None:
        consulta = consulta.filter(Cuenta.activo == activo)
    if tipo:
        consulta = consulta.filter(Cuenta.tipo == tipo.upper())
    if es_banco is not None:
        consulta = consulta.filter(Cuenta.es_banco == es_banco)
    if q:
        patron = f"%{q}%"
        consulta = consulta.filter(
            or_(Cuenta.codigo.ilike(patron), Cuenta.nombre.ilike(patron))
        )
    return consulta.order_by(Cuenta.codigo).all()


@router.post("", response_model=CuentaOut, status_code=201)
def crear_cuenta(datos: CuentaCreate, db: Session = Depends(get_db)):
    if db.query(Cuenta).filter_by(codigo=datos.codigo).first():
        raise HTTPException(409, f"Ya existe una cuenta con el código {datos.codigo}.")
    cuenta = Cuenta(**datos.model_dump())
    db.add(cuenta)
    db.commit()
    db.refresh(cuenta)
    return cuenta


@router.get("/{cuenta_id}", response_model=CuentaOut)
def obtener_cuenta(cuenta_id: int, db: Session = Depends(get_db)):
    cuenta = db.get(Cuenta, cuenta_id)
    if cuenta is None:
        raise HTTPException(404, "Cuenta no encontrada.")
    return cuenta


@router.put("/{cuenta_id}", response_model=CuentaOut)
def actualizar_cuenta(cuenta_id: int, datos: CuentaUpdate, db: Session = Depends(get_db)):
    cuenta = db.get(Cuenta, cuenta_id)
    if cuenta is None:
        raise HTTPException(404, "Cuenta no encontrada.")
    for campo, valor in datos.model_dump(exclude_unset=True).items():
        setattr(cuenta, campo, valor)
    db.commit()
    db.refresh(cuenta)
    return cuenta


@router.delete("/{cuenta_id}", status_code=204)
def desactivar_cuenta(cuenta_id: int, db: Session = Depends(get_db)):
    cuenta = db.get(Cuenta, cuenta_id)
    if cuenta is None:
        raise HTTPException(404, "Cuenta no encontrada.")
    cuenta.activo = False  # borrado lógico: nunca se borra físicamente
    db.commit()
