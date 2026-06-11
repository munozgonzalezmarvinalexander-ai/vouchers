"""
services/auditoria.py
---------------------
Un ayudante para registrar acciones en la bitácora del voucher. No hace commit:
lo hace quien lo llama, para que la auditoría quede en la misma transacción que
la acción que la origina (o todo se guarda, o nada).

El campo `usuario` queda como "sistema" por ahora; cuando agreguemos login
(Etapa 6) se pondrá el usuario real.
"""

from app.models import Auditoria


def registrar(db, voucher_id: int, accion: str, detalle: str | None = None, usuario: str = "sistema"):
    db.add(Auditoria(voucher_id=voucher_id, accion=accion, detalle=detalle, usuario=usuario))
