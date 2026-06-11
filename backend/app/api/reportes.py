"""
api/reportes.py
---------------
Reportes:
  GET /reportes/libro-vouchers         -> lista + total (JSON)
  GET /reportes/libro-vouchers/excel   -> el mismo libro en .xlsx
  GET /reportes/totales-por-partida    -> cuánto se gastó por cada partida
"""

from datetime import date

from fastapi import APIRouter, Depends
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import LibroOut, TotalPartidaOut
from app.services import reportes

router = APIRouter(prefix="/reportes", tags=["Reportes"])


@router.get("/libro-vouchers", response_model=LibroOut)
def libro(
    proyecto_id: int | None = None,
    desde: date | None = None,
    hasta: date | None = None,
    db: Session = Depends(get_db),
):
    vouchers, total = reportes.libro_vouchers(db, proyecto_id, desde, hasta)
    return {"conteo": len(vouchers), "total": total, "vouchers": vouchers}


@router.get("/libro-vouchers/excel")
def libro_excel(
    proyecto_id: int | None = None,
    desde: date | None = None,
    hasta: date | None = None,
    db: Session = Depends(get_db),
):
    vouchers, total = reportes.libro_vouchers(db, proyecto_id, desde, hasta)
    data = reportes.libro_excel(vouchers, total)
    return Response(
        content=data,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": 'attachment; filename="libro-vouchers.xlsx"'},
    )


@router.get("/totales-por-partida", response_model=list[TotalPartidaOut])
def totales_por_partida(
    proyecto_id: int | None = None,
    desde: date | None = None,
    hasta: date | None = None,
    db: Session = Depends(get_db),
):
    return reportes.totales_por_partida(db, proyecto_id, desde, hasta)
