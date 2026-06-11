"""
services/vouchers.py
--------------------
La lógica de negocio de los vouchers. Aquí viven las reglas que el Excel no
podía garantizar: que un voucher no se guarde descuadrado, que se numere solo,
y que solo avance por su flujo de estados de forma válida.

Los routers (capa HTTP) llaman a estas funciones; no contienen reglas.
"""

from app.models import Cuenta, Proyecto, Voucher, VoucherDetalle
from app.services.auditoria import registrar
from app.services.cuadre import calcular_totales, esta_cuadrado, validar_lineas
from app.services.numeracion import siguiente_numero

# Flujo de estados permitido. Cada estado dice a cuáles puede pasar.
#   BORRADOR  -> se puede revisar o anular
#   REVISADO  -> se puede autorizar, devolver a borrador o anular
#   AUTORIZADO-> solo se puede anular (ya no se edita)
#   ANULADO   -> estado final
TRANSICIONES = {
    "BORRADOR": {"REVISADO", "ANULADO"},
    "REVISADO": {"AUTORIZADO", "BORRADOR", "ANULADO"},
    "AUTORIZADO": {"ANULADO"},
    "ANULADO": set(),
}


class ErrorNegocio(Exception):
    """Una regla de negocio no se cumplió. El router lo traduce a HTTP 400."""


def _construir_detalles(db, voucher: Voucher, detalles_in) -> None:
    """Crea las líneas del voucher, validando que cada cuenta exista."""
    for i, d in enumerate(detalles_in):
        cuenta = db.get(Cuenta, d.cuenta_id)
        if cuenta is None:
            raise ErrorNegocio(f"La cuenta con id {d.cuenta_id} no existe en el catálogo.")
        voucher.detalles.append(
            VoucherDetalle(
                cuenta_id=cuenta.id,
                # Si no mandan descripción, se usa el nombre limpio de la cuenta.
                descripcion=(d.descripcion or cuenta.nombre),
                debe=d.debe or 0,
                haber=d.haber or 0,
                orden=d.orden if d.orden is not None else i,
            )
        )


def crear_voucher(db, datos) -> Voucher:
    proyecto = db.get(Proyecto, datos.proyecto_id)
    if proyecto is None:
        raise ErrorNegocio("El proyecto indicado no existe.")

    errores = validar_lineas(datos.detalles)
    if errores:
        raise ErrorNegocio(" ".join(errores))

    total_debe, total_haber, diferencia = calcular_totales(datos.detalles)

    estado = (datos.estado or "BORRADOR").upper()
    if estado not in ("BORRADOR", "REVISADO"):
        raise ErrorNegocio("Un voucher nuevo solo puede nacer como BORRADOR o REVISADO.")
    # La regla central: solo un BORRADOR puede quedar descuadrado (trabajo en curso).
    if estado == "REVISADO" and diferencia != 0:
        raise ErrorNegocio(
            f"El voucher no cuadra: debe {total_debe}, haber {total_haber}, "
            f"diferencia {diferencia}."
        )

    voucher = Voucher(
        proyecto_id=proyecto.id,
        numero=siguiente_numero(db, proyecto, datos.fecha.year),
        fecha=datos.fecha,
        concepto=datos.concepto.strip(),
        estado=estado,
        total=total_debe,
        elaborado_por_id=datos.elaborado_por_id,
        revisado_por_id=datos.revisado_por_id,
        autorizado_por_id=datos.autorizado_por_id,
    )
    _construir_detalles(db, voucher, datos.detalles)

    db.add(voucher)
    db.flush()  # asigna el id sin cerrar la transacción
    registrar(db, voucher.id, "CREADO")
    db.commit()
    db.refresh(voucher)
    return voucher


def actualizar_voucher(db, voucher: Voucher, datos) -> Voucher:
    if voucher.estado != "BORRADOR":
        raise ErrorNegocio("Solo se puede editar un voucher en estado BORRADOR.")

    errores = validar_lineas(datos.detalles)
    if errores:
        raise ErrorNegocio(" ".join(errores))

    total_debe, _, _ = calcular_totales(datos.detalles)

    voucher.fecha = datos.fecha
    voucher.concepto = datos.concepto.strip()
    voucher.total = total_debe
    voucher.elaborado_por_id = datos.elaborado_por_id
    voucher.revisado_por_id = datos.revisado_por_id
    voucher.autorizado_por_id = datos.autorizado_por_id

    voucher.detalles.clear()  # delete-orphan elimina las líneas anteriores
    _construir_detalles(db, voucher, datos.detalles)

    registrar(db, voucher.id, "EDITADO")
    db.commit()
    db.refresh(voucher)
    return voucher


def cambiar_estado(db, voucher: Voucher, destino: str) -> Voucher:
    destino = destino.upper()
    permitidos = TRANSICIONES.get(voucher.estado, set())
    if destino not in permitidos:
        raise ErrorNegocio(f"No se puede pasar de {voucher.estado} a {destino}.")
    # No se deja revisar algo que no cuadra.
    if destino == "REVISADO" and not esta_cuadrado(voucher.detalles):
        raise ErrorNegocio("No se puede revisar un voucher que no cuadra.")
    voucher.estado = destino
    registrar(db, voucher.id, destino)
    db.commit()
    db.refresh(voucher)
    return voucher
