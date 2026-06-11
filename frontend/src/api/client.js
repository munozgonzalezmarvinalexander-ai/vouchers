// Cliente HTTP único. La URL del backend viene de la variable VITE_API_URL
// (ver .env). Así el mismo frontend sirve para local o para producción.
const BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'

async function req(path, options = {}) {
  const res = await fetch(`${BASE}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  })
  if (!res.ok) {
    let detalle = `Error ${res.status}`
    try {
      const j = await res.json()
      detalle = j.detail || detalle
    } catch {
      /* respuesta sin cuerpo JSON */
    }
    throw new Error(detalle)
  }
  if (res.status === 204) return null
  return res.json()
}

function query(obj = {}) {
  const limpio = {}
  for (const [k, v] of Object.entries(obj)) {
    if (v !== '' && v != null) limpio[k] = v
  }
  return new URLSearchParams(limpio).toString()
}

export const api = {
  proyectos: () => req('/proyectos'),
  firmantes: (rol) => req(`/firmantes${rol ? `?rol=${rol}` : ''}`),
  cuentas: (q) => req(`/cuentas?${query({ q })}`),
  favoritas: (proyectoId, limite = 15) =>
    req(`/proyectos/${proyectoId}/cuentas-frecuentes?${query({ limite })}`),
  listarVouchers: (filtros) => req(`/vouchers?${query(filtros)}`),
  obtenerVoucher: (id) => req(`/vouchers/${id}`),
  crearVoucher: (data) => req('/vouchers', { method: 'POST', body: JSON.stringify(data) }),
  actualizarVoucher: (id, data) =>
    req(`/vouchers/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
  cambiarEstado: (id, estado) =>
    req(`/vouchers/${id}/estado`, { method: 'PATCH', body: JSON.stringify({ estado }) }),
  auditoria: (id) => req(`/vouchers/${id}/auditoria`),
  revisarOrtografia: (texto) =>
    req('/ortografia/revisar', { method: 'POST', body: JSON.stringify({ texto }) }),
  libroVouchers: (filtros) => req(`/reportes/libro-vouchers?${query(filtros)}`),
  totalesPorPartida: (filtros) => req(`/reportes/totales-por-partida?${query(filtros)}`),
}

// URL del libro de vouchers en Excel (se abre/descarga directo).
export const libroExcelUrl = (filtros = {}) =>
  `${BASE}/reportes/libro-vouchers/excel?${query(filtros)}`

// URLs de documentos del voucher. Se abren directo en el navegador:
//  - imprimir: muestra el voucher y abre el diálogo de impresión (no descarga).
//  - pdf / excel: descargan el archivo.
export const docUrls = (id) => ({
  imprimir: `${BASE}/vouchers/${id}/html?imprimir=1`,
  vistaPrevia: `${BASE}/vouchers/${id}/html`,
  pdf: `${BASE}/vouchers/${id}/pdf?descargar=1`,
  excel: `${BASE}/vouchers/${id}/excel`,
})
