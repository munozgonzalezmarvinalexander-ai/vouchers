"""
api/proyectos.py
----------------
Endpoints de proyectos/fondos. Incluye las cuentas FAVORITAS de cada proyecto,
que ya no se configuran a mano: se calculan por uso (las más usadas), así que
la lista se alimenta sola conforme creas vouchers.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Proyecto
from app.schemas import (
    CuentaFrecuenteOut, CuentaOut, ProyectoCreate, ProyectoOut, ProyectoUpdate,
)
from app.services.favoritos import cuentas_frecuentes

router = APIRouter(prefix="/proyectos", tags=["Proyectos"])


@router.get("", response_model=list[ProyectoOut])
def listar_proyectos(activo: bool | None = True, db: Session = Depends(get_db)):
    consulta = db.query(Proyecto)
    if activo is not None:
        consulta = consulta.filter(Proyecto.activo == activo)
    return consulta.order_by(Proyecto.nombre).all()


@router.post("", response_model=ProyectoOut, status_code=201)
def crear_proyecto(datos: ProyectoCreate, db: Session = Depends(get_db)):
    if db.query(Proyecto).filter_by(codigo=datos.codigo).first():
        raise HTTPException(409, f"Ya existe un proyecto con el código {datos.codigo}.")
    proyecto = Proyecto(**datos.model_dump())
    db.add(proyecto)
    db.commit()
    db.refresh(proyecto)
    return proyecto


@router.get("/{proyecto_id}", response_model=ProyectoOut)
def obtener_proyecto(proyecto_id: int, db: Session = Depends(get_db)):
    proyecto = db.get(Proyecto, proyecto_id)
    if proyecto is None:
        raise HTTPException(404, "Proyecto no encontrado.")
    return proyecto


@router.put("/{proyecto_id}", response_model=ProyectoOut)
def actualizar_proyecto(proyecto_id: int, datos: ProyectoUpdate, db: Session = Depends(get_db)):
    proyecto = db.get(Proyecto, proyecto_id)
    if proyecto is None:
        raise HTTPException(404, "Proyecto no encontrado.")
    for campo, valor in datos.model_dump(exclude_unset=True).items():
        setattr(proyecto, campo, valor)
    db.commit()
    db.refresh(proyecto)
    return proyecto


@router.get("/{proyecto_id}/cuentas-frecuentes", response_model=list[CuentaFrecuenteOut])
def favoritas_del_proyecto(
    proyecto_id: int,
    limite: int = Query(15, ge=1, le=50, description="Cuántas favoritas devolver"),
    db: Session = Depends(get_db),
):
    """Las cuentas más usadas de un proyecto (favoritos automáticos).

    Se calculan desde el historial de vouchers. Si el proyecto aún no tiene
    vouchers, la lista viene vacía y se va llenando con el uso.
    """
    if db.get(Proyecto, proyecto_id) is None:
        raise HTTPException(404, "Proyecto no encontrado.")
    filas = cuentas_frecuentes(db, proyecto_id, limite)
    # Cada fila es (Cuenta, usos): combinamos los datos de la cuenta con su conteo.
    return [
        CuentaFrecuenteOut(**CuentaOut.model_validate(cuenta).model_dump(), usos=usos)
        for cuenta, usos in filas
    ]
