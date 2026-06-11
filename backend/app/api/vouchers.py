"""
api/vouchers.py
---------------
Endpoints de vouchers. Fíjate en el patrón: el router NO valida el cuadre ni
arma el número. Solo recibe la petición, llama al servicio y traduce los
errores de negocio (ErrorNegocio) a respuestas HTTP 400.
"""

from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Voucher
from app.schemas import (
    AuditoriaOut, CambiarEstadoIn, VoucherCreate, VoucherListItem, VoucherOut, VoucherUpdate,
)
from app.services import vouchers as servicio
from app.services.vouchers import ErrorNegocio

router = APIRouter(prefix="/vouchers", tags=["Vouchers"])


def _obtener(db: Session, voucher_id: int) -> Voucher:
    voucher = db.get(Voucher, voucher_id)
    if voucher is None:
        raise HTTPException(404, "Voucher no encontrado.")
    return voucher


@router.post("", response_model=VoucherOut, status_code=201)
def crear_voucher(datos: VoucherCreate, db: Session = Depends(get_db)):
    try:
        return servicio.crear_voucher(db, datos)
    except ErrorNegocio as e:
        raise HTTPException(400, str(e))


@router.get("", response_model=list[VoucherListItem])
def listar_vouchers(
    proyecto_id: int | None = None,
    estado: str | None = None,
    q: str | None = Query(None, description="Busca en el concepto"),
    desde: date | None = None,
    hasta: date | None = None,
    db: Session = Depends(get_db),
):
    consulta = db.query(Voucher)
    if proyecto_id:
        consulta = consulta.filter(Voucher.proyecto_id == proyecto_id)
    if estado:
        consulta = consulta.filter(Voucher.estado == estado.upper())
    if q:
        consulta = consulta.filter(Voucher.concepto.ilike(f"%{q}%"))
    if desde:
        consulta = consulta.filter(Voucher.fecha >= desde)
    if hasta:
        consulta = consulta.filter(Voucher.fecha <= hasta)
    return consulta.order_by(Voucher.fecha.desc(), Voucher.id.desc()).all()


@router.get("/{voucher_id}", response_model=VoucherOut)
def obtener_voucher(voucher_id: int, db: Session = Depends(get_db)):
    return _obtener(db, voucher_id)


@router.put("/{voucher_id}", response_model=VoucherOut)
def actualizar_voucher(voucher_id: int, datos: VoucherUpdate, db: Session = Depends(get_db)):
    voucher = _obtener(db, voucher_id)
    try:
        return servicio.actualizar_voucher(db, voucher, datos)
    except ErrorNegocio as e:
        raise HTTPException(400, str(e))


@router.patch("/{voucher_id}/estado", response_model=VoucherOut)
def cambiar_estado(voucher_id: int, datos: CambiarEstadoIn, db: Session = Depends(get_db)):
    voucher = _obtener(db, voucher_id)
    try:
        return servicio.cambiar_estado(db, voucher, datos.estado)
    except ErrorNegocio as e:
        raise HTTPException(400, str(e))


@router.delete("/{voucher_id}", response_model=VoucherOut)
def anular_voucher(voucher_id: int, db: Session = Depends(get_db)):
    """Anular = borrado lógico. El voucher conserva su número e historial."""
    voucher = _obtener(db, voucher_id)
    try:
        return servicio.cambiar_estado(db, voucher, "ANULADO")
    except ErrorNegocio as e:
        raise HTTPException(400, str(e))


@router.get("/{voucher_id}/auditoria", response_model=list[AuditoriaOut])
def auditoria_voucher(voucher_id: int, db: Session = Depends(get_db)):
    """Historial de acciones del voucher (más reciente primero)."""
    voucher = _obtener(db, voucher_id)
    return list(reversed(voucher.auditorias))
