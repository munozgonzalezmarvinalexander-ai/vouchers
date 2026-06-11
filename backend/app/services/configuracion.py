"""
services/configuracion.py
-------------------------
Lee y crea la configuración de impresión (una sola fila, id=1). Si no existe,
la crea con los valores por defecto. Convierte los números a estilos CSS con
sus unidades para la plantilla.
"""

from app.models import Configuracion

CAMPOS = (
    "fuente_pt",
    "espacio_concepto_mm",
    "espacio_firmas_mm",
    "margen_inferior_mm",
    "margen_lateral_mm",
)


def obtener(db) -> Configuracion:
    cfg = db.get(Configuracion, 1)
    if cfg is None:
        cfg = Configuracion(id=1)
        db.add(cfg)
        db.commit()
        db.refresh(cfg)
    return cfg


def como_dict(cfg) -> dict:
    return {campo: getattr(cfg, campo) for campo in CAMPOS}


def estilos(cfg_dict: dict) -> dict:
    """Convierte los números de la config en variables CSS con unidades."""
    return {
        "fs": f"{cfg_dict['fuente_pt']}pt",
        "mb": f"{cfg_dict['margen_inferior_mm']}mm",
        "ml": f"{cfg_dict['margen_lateral_mm']}mm",
        "g_concepto": f"{cfg_dict['espacio_concepto_mm']}mm",
        "g_firmas": f"{cfg_dict['espacio_firmas_mm']}mm",
    }
