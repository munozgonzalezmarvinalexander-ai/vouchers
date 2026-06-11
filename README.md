# Sistema de Vouchers Contables

Aplicación web para registrar, controlar e imprimir **vouchers contables**
(partidas de doble entrada) de una ONG, reemplazando el flujo anterior en Excel.
Pensada para que varias computadoras la usen al mismo tiempo, abriendo una URL y
compartiendo una sola base de datos.

## Qué resuelve

- **Cuadre garantizado:** un voucher no se puede revisar/autorizar si el debe no
  iguala al haber. El Excel no lo impedía.
- **Numeración automática** por proyecto y año (ej. `KNH-SALUD-2026-0001`).
- **Flujo de estados** con control: `BORRADOR → REVISADO → AUTORIZADO`, más
  `ANULADO`. Un voucher autorizado ya no se edita.
- **Impresión directa** (sin descargar archivos), más exportación a **PDF** y
  **Excel** con el formato del voucher (concepto, líneas, totales y tres firmas).
- **Reportes:** libro de vouchers y totales por partida (con filtros y Excel).
- **Ortografía** del texto libre, con un diccionario propio del dominio.
- **Auditoría:** historial de cada acción sobre el voucher.

## Estructura

```
.
├── backend/      API en FastAPI (lógica, PDF/Excel, reportes, catálogo)
├── frontend/     Interfaz en React + Vite + Tailwind
├── docs/         Análisis y diseño del sistema
├── GUIA-DESPLIEGUE.md   Cómo ponerlo en línea, paso a paso
└── README.md     Este archivo
```

## Tecnologías

- **Backend:** FastAPI · SQLAlchemy 2.0 · Pydantic · WeasyPrint (PDF) ·
  openpyxl (Excel) · pyspellchecker (ortografía) · pytest.
- **Frontend:** React · Vite · Tailwind CSS · React Router.
- **Base de datos:** PostgreSQL (Neon en producción) o SQLite (local).
  El mismo código sirve para ambos: solo cambia la variable `DATABASE_URL`.

## Cómo correrlo

- **Ponerlo en línea (producción):** sigue **`GUIA-DESPLIEGUE.md`** — base de
  datos en Neon, backend en Render (Docker) y frontend en Vercel, todo gratis.
- **Probarlo localmente:** ver la última sección de la misma guía.

## Diseño

El documento `docs/analisis-y-diseno-sistema-vouchers.md` explica el análisis
funcional, el modelo de datos y las decisiones técnicas (por qué el banco es una
línea más y no un caso especial, por qué las cuentas frecuentes se calculan por
uso, etc.).
