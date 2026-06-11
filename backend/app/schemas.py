"""
schemas.py
----------
Los "contratos" de la API: qué datos entran (Create/Update) y qué datos salen
(Out). Son clases Pydantic. FastAPI las usa para validar automáticamente cada
petición y para documentar la API en /docs.

`from_attributes=True` permite construir la respuesta directamente desde un
objeto de SQLAlchemy (lee sus atributos, incluidas las propiedades calculadas).
"""

from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


# ---------- Catálogo de cuentas ----------
class CuentaBase(BaseModel):
    codigo: str
    nombre: str
    tipo: str
    naturaleza: str = "DEUDORA"
    es_banco: bool = False
    numero_cuenta: str | None = None
    resultado: str | None = None
    activo: bool = True


class CuentaCreate(CuentaBase):
    pass


class CuentaUpdate(BaseModel):
    # Todo opcional: se actualiza solo lo que venga.
    nombre: str | None = None
    tipo: str | None = None
    naturaleza: str | None = None
    es_banco: bool | None = None
    numero_cuenta: str | None = None
    resultado: str | None = None
    activo: bool | None = None


class CuentaOut(CuentaBase):
    model_config = ConfigDict(from_attributes=True)
    id: int


class CuentaFrecuenteOut(CuentaOut):
    """Una cuenta favorita (calculada por uso), con su número de usos."""
    usos: int


# ---------- Firmantes ----------
class FirmanteOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    nombre: str
    cargo: str | None = None
    rol_firma: str
    activo: bool


# ---------- Proyectos ----------
class ProyectoBase(BaseModel):
    codigo: str
    nombre: str
    donante: str | None = None
    activo: bool = True


class ProyectoCreate(ProyectoBase):
    pass


class ProyectoUpdate(BaseModel):
    nombre: str | None = None
    donante: str | None = None
    activo: bool | None = None


class ProyectoOut(ProyectoBase):
    model_config = ConfigDict(from_attributes=True)
    id: int


# ---------- Vouchers ----------
class VoucherDetalleIn(BaseModel):
    cuenta_id: int
    descripcion: str | None = None
    debe: Decimal = Decimal("0")
    haber: Decimal = Decimal("0")
    orden: int | None = None


class VoucherDetalleOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    cuenta_id: int
    descripcion: str | None = None
    debe: Decimal
    haber: Decimal
    orden: int
    cuenta: CuentaOut | None = None


class VoucherCreate(BaseModel):
    proyecto_id: int
    fecha: date
    concepto: str = Field(min_length=1)
    detalles: list[VoucherDetalleIn] = Field(min_length=1)
    elaborado_por_id: int | None = None
    revisado_por_id: int | None = None
    autorizado_por_id: int | None = None
    estado: str = "BORRADOR"


class VoucherUpdate(BaseModel):
    fecha: date
    concepto: str = Field(min_length=1)
    detalles: list[VoucherDetalleIn] = Field(min_length=1)
    elaborado_por_id: int | None = None
    revisado_por_id: int | None = None
    autorizado_por_id: int | None = None


class CambiarEstadoIn(BaseModel):
    estado: str


class VoucherListItem(BaseModel):
    """Versión ligera para listados (sin las líneas)."""
    model_config = ConfigDict(from_attributes=True)
    id: int
    numero: str
    proyecto_id: int
    fecha: date
    concepto: str
    estado: str
    total: Decimal


class VoucherOut(VoucherListItem):
    """Versión completa para el detalle de un voucher."""
    total_debe: Decimal
    total_haber: Decimal
    detalles: list[VoucherDetalleOut] = []
    banco: CuentaOut | None = None
    elaborado_por: FirmanteOut | None = None
    revisado_por: FirmanteOut | None = None
    autorizado_por: FirmanteOut | None = None
    created_at: datetime
    updated_at: datetime | None = None


# ---------- Auditoría ----------
class AuditoriaOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    accion: str
    usuario: str | None = None
    detalle: str | None = None
    fecha: datetime


# ---------- Reportes ----------
class LibroOut(BaseModel):
    conteo: int
    total: Decimal
    vouchers: list[VoucherListItem]


class TotalPartidaOut(BaseModel):
    codigo: str
    nombre: str
    total: Decimal
    veces: int


class ConfiguracionImpresion(BaseModel):
    """Ajustes de impresión del voucher (en pt y mm)."""
    fuente_pt: float = 12
    espacio_concepto_mm: float = 14
    espacio_firmas_mm: float = 28
    margen_inferior_mm: float = 15
    margen_lateral_mm: float = 18

    model_config = ConfigDict(from_attributes=True)
