"""
api/documentos.py
-----------------
Endpoints para imprimir y exportar un voucher.

  GET /vouchers/{id}/html?imprimir=1  -> HTML del voucher. Con imprimir=1 abre
        el diálogo de impresión solo (NO descarga ningún archivo).
  GET /vouchers/{id}/pdf?descargar=1  -> el voucher en PDF.
  GET /vouchers/{id}/excel            -> el voucher en .xlsx.
"""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import HTMLResponse, Response
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Voucher
from app.services import configuracion as cfg
from app.services import documentos as doc

router = APIRouter(prefix="/vouchers", tags=["Documentos"])


def _voucher(db: Session, voucher_id: int) -> Voucher:
    v = db.get(Voucher, voucher_id)
    if v is None:
        raise HTTPException(404, "Voucher no encontrado.")
    return v


@router.get("/{voucher_id}/html", response_class=HTMLResponse)
def voucher_html(voucher_id: int, imprimir: bool = False, db: Session = Depends(get_db)):
    """Vista imprimible. Con ?imprimir=1 dispara la impresión del navegador.
    Usa los ajustes guardados en Configuración de impresión."""
    v = _voucher(db, voucher_id)
    config = cfg.como_dict(cfg.obtener(db))
    return HTMLResponse(doc.render_html(v, config, auto_print=imprimir))


@router.get("/{voucher_id}/pdf")
def voucher_pdf(voucher_id: int, descargar: bool = False, db: Session = Depends(get_db)):
    v = _voucher(db, voucher_id)
    config = cfg.como_dict(cfg.obtener(db))
    try:
        pdf = doc.render_pdf(v, config)
    except RuntimeError as e:
        raise HTTPException(503, str(e))
    disposicion = "attachment" if descargar else "inline"
    return Response(
        content=pdf,
        media_type="application/pdf",
        headers={"Content-Disposition": f'{disposicion}; filename="voucher-{v.numero}.pdf"'},
    )


@router.get("/{voucher_id}/excel")
def voucher_excel(voucher_id: int, db: Session = Depends(get_db)):
    v = _voucher(db, voucher_id)
    data = doc.generar_excel(v)
    return Response(
        content=data,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="voucher-{v.numero}.xlsx"'},
    )
