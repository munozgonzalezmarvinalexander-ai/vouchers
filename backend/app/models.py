"""
models.py
---------
El modelo entidad-relación, hecho clases. En la Etapa 1 definimos las tablas
del catálogo central. Las tablas de vouchers, auditoría y usuarios llegan en
la Etapa 2 (API).

Tablas:
  - Cuenta          : catálogo único de partidas y cuentas (reemplaza los 13
                      mini-catálogos del Excel).
  - Proyecto        : cada fondo/donante (una hoja del Excel = un proyecto).
  - Firmante        : quién elabora / revisa / autoriza.

  Nota: los "favoritos" ya NO son una tabla. Se calculan automáticamente
  según el uso (las cuentas más usadas por proyecto). Ver services/favoritos.py.
"""

from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    Boolean, Date, DateTime, ForeignKey, Integer, Numeric, String, Text, func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

# Estados posibles de un voucher (su ciclo de vida).
ESTADOS_VOUCHER = ("BORRADOR", "REVISADO", "AUTORIZADO", "ANULADO")


class Cuenta(Base):
    __tablename__ = "cuentas"

    id: Mapped[int] = mapped_column(primary_key=True)
    codigo: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    nombre: Mapped[str] = mapped_column(String(255))
    # GASTO | BANCO | ACTIVO | PASIVO
    tipo: Mapped[str] = mapped_column(String(20))
    # DEUDORA | ACREEDORA  (de qué lado suma normalmente la cuenta)
    naturaleza: Mapped[str] = mapped_column(String(12))
    es_banco: Mapped[bool] = mapped_column(Boolean, default=False)
    numero_cuenta: Mapped[str | None] = mapped_column(String(40), nullable=True)
    # Código de resultado / marco lógico (R2, GT6, 1.1.1.5, ...), opcional
    resultado: Mapped[str | None] = mapped_column(String(40), nullable=True)
    activo: Mapped[bool] = mapped_column(Boolean, default=True)

    def __repr__(self) -> str:
        return f"<Cuenta {self.codigo} {self.nombre!r}>"


class Proyecto(Base):
    __tablename__ = "proyectos"

    id: Mapped[int] = mapped_column(primary_key=True)
    codigo: Mapped[str] = mapped_column(String(40), unique=True, index=True)
    nombre: Mapped[str] = mapped_column(String(120), unique=True)
    donante: Mapped[str | None] = mapped_column(String(120), nullable=True)
    activo: Mapped[bool] = mapped_column(Boolean, default=True)

    def __repr__(self) -> str:
        return f"<Proyecto {self.nombre!r}>"


class Firmante(Base):
    __tablename__ = "firmantes"

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(120))
    cargo: Mapped[str | None] = mapped_column(String(120), nullable=True)
    # ELABORA | REVISA | AUTORIZA
    rol_firma: Mapped[str] = mapped_column(String(12))
    activo: Mapped[bool] = mapped_column(Boolean, default=True)

    def __repr__(self) -> str:
        return f"<Firmante {self.nombre!r} ({self.rol_firma})>"


class Voucher(Base):
    """Un asiento contable de doble entrada (la partida contable / voucher)."""
    __tablename__ = "vouchers"

    id: Mapped[int] = mapped_column(primary_key=True)
    proyecto_id: Mapped[int] = mapped_column(ForeignKey("proyectos.id"))
    numero: Mapped[str] = mapped_column(String(40), unique=True, index=True)
    fecha: Mapped[date] = mapped_column(Date)
    concepto: Mapped[str] = mapped_column(Text)
    total: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0)
    estado: Mapped[str] = mapped_column(String(12), default="BORRADOR", index=True)

    # Las tres firmas del voucher (apuntan al catálogo de firmantes).
    elaborado_por_id: Mapped[int | None] = mapped_column(ForeignKey("firmantes.id"), nullable=True)
    revisado_por_id: Mapped[int | None] = mapped_column(ForeignKey("firmantes.id"), nullable=True)
    autorizado_por_id: Mapped[int | None] = mapped_column(ForeignKey("firmantes.id"), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), onupdate=func.now(), nullable=True)

    proyecto: Mapped["Proyecto"] = relationship()
    detalles: Mapped[list["VoucherDetalle"]] = relationship(
        back_populates="voucher",
        cascade="all, delete-orphan",   # borrar el voucher borra sus líneas
        order_by="VoucherDetalle.orden",
    )
    auditorias: Mapped[list["Auditoria"]] = relationship(
        back_populates="voucher", order_by="Auditoria.fecha"
    )
    # Tres relaciones al mismo catálogo: hay que decir por cuál FK va cada una.
    elaborado_por: Mapped["Firmante | None"] = relationship("Firmante", foreign_keys=[elaborado_por_id])
    revisado_por: Mapped["Firmante | None"] = relationship("Firmante", foreign_keys=[revisado_por_id])
    autorizado_por: Mapped["Firmante | None"] = relationship("Firmante", foreign_keys=[autorizado_por_id])

    # Propiedades calculadas (no se guardan; se derivan de las líneas).
    @property
    def total_debe(self) -> Decimal:
        return sum((d.debe or Decimal("0") for d in self.detalles), Decimal("0"))

    @property
    def total_haber(self) -> Decimal:
        return sum((d.haber or Decimal("0") for d in self.detalles), Decimal("0"))

    @property
    def banco(self) -> "Cuenta | None":
        # El banco no es un caso especial: es la línea cuya cuenta es de banco.
        return next((d.cuenta for d in self.detalles if d.cuenta and d.cuenta.es_banco), None)

    def __repr__(self) -> str:
        return f"<Voucher {self.numero} {self.estado}>"


class VoucherDetalle(Base):
    """Una línea del voucher: una cuenta con un monto al debe O al haber."""
    __tablename__ = "voucher_detalles"

    id: Mapped[int] = mapped_column(primary_key=True)
    voucher_id: Mapped[int] = mapped_column(ForeignKey("vouchers.id"))
    cuenta_id: Mapped[int] = mapped_column(ForeignKey("cuentas.id"))
    # Por defecto es el nombre de la cuenta, pero se puede personalizar
    # (ej. "DIETAS" -> "DIETAS 1 COORDINADORA").
    descripcion: Mapped[str | None] = mapped_column(String(255), nullable=True)
    debe: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0)
    haber: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0)
    orden: Mapped[int] = mapped_column(Integer, default=0)

    voucher: Mapped["Voucher"] = relationship(back_populates="detalles")
    cuenta: Mapped["Cuenta"] = relationship()


class Auditoria(Base):
    """Bitácora de acciones sobre un voucher (historial/trazabilidad).

    El campo 'usuario' queda como 'sistema' por ahora; cuando se agregue el
    inicio de sesión (Etapa 6) guardará el usuario real que hizo la acción.
    """
    __tablename__ = "auditorias"

    id: Mapped[int] = mapped_column(primary_key=True)
    voucher_id: Mapped[int] = mapped_column(ForeignKey("vouchers.id"))
    # CREADO | EDITADO | REVISADO | AUTORIZADO | BORRADOR | ANULADO
    accion: Mapped[str] = mapped_column(String(20))
    usuario: Mapped[str | None] = mapped_column(String(120), nullable=True)
    detalle: Mapped[str | None] = mapped_column(String(255), nullable=True)
    fecha: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    voucher: Mapped["Voucher"] = relationship(back_populates="auditorias")

    def __repr__(self) -> str:
        return f"<Auditoria {self.accion} voucher={self.voucher_id}>"
