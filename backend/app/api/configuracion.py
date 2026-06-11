"""
api/configuracion.py
--------------------
Lee y guarda los ajustes de impresión, y ofrece una vista previa en vivo con un
voucher de ejemplo (sin guardar) para afinar los valores antes de imprimir.

  GET /configuracion           -> ajustes actuales
  PUT /configuracion           -> guarda los ajustes (compartidos por todos)
  GET /configuracion/preview   -> HTML de muestra con los valores que se le pasen
"""

from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import ConfiguracionImpresion
from app.services import configuracion as cfg
from app.services import documentos as doc

router = APIRouter(prefix="/configuracion", tags=["Configuración"])


@router.get("", response_model=ConfiguracionImpresion)
def obtener(db: Session = Depends(get_db)):
    return cfg.obtener(db)


@router.put("", response_model=ConfiguracionImpresion)
def guardar(datos: ConfiguracionImpresion, db: Session = Depends(get_db)):
    config = cfg.obtener(db)
    for campo, valor in datos.model_dump().items():
        setattr(config, campo, valor)
    db.commit()
    db.refresh(config)
    return config


@router.get("/preview", response_class=HTMLResponse)
def preview(
    fuente_pt: float = 12,
    espacio_concepto_mm: float = 14,
    espacio_firmas_mm: float = 28,
    margen_inferior_mm: float = 15,
    margen_lateral_mm: float = 18,
):
    config = {
        "fuente_pt": fuente_pt,
        "espacio_concepto_mm": espacio_concepto_mm,
        "espacio_firmas_mm": espacio_firmas_mm,
        "margen_inferior_mm": margen_inferior_mm,
        "margen_lateral_mm": margen_lateral_mm,
    }
    return HTMLResponse(doc.render_muestra(config))
