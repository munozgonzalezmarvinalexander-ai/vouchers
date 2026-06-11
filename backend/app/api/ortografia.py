"""
api/ortografia.py
-----------------
Endpoint para revisar la ortografía de un texto (el concepto del voucher u otro
texto libre). No toca la base de datos.
"""

from fastapi import APIRouter
from pydantic import BaseModel

from app.services.ortografia import revisar

router = APIRouter(prefix="/ortografia", tags=["Ortografía"])


class TextoIn(BaseModel):
    texto: str


@router.post("/revisar")
def revisar_texto(datos: TextoIn):
    return {"palabras": revisar(datos.texto)}
