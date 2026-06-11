"""
api/firmantes.py
----------------
Endpoint para listar los firmantes (quién elabora / revisa / autoriza),
usado para llenar los selectores del formulario de voucher.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Firmante
from app.schemas import FirmanteOut

router = APIRouter(prefix="/firmantes", tags=["Firmantes"])


@router.get("", response_model=list[FirmanteOut])
def listar_firmantes(rol: str | None = None, db: Session = Depends(get_db)):
    consulta = db.query(Firmante).filter(Firmante.activo.is_(True))
    if rol:
        consulta = consulta.filter(Firmante.rol_firma == rol.upper())
    return consulta.order_by(Firmante.nombre).all()
