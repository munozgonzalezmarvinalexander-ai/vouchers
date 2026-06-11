import { useEffect, useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { api } from '../api/client.js'
import { money } from '../lib/format.js'
import EstadoBadge from '../components/EstadoBadge.jsx'

const ESTADOS = ['', 'BORRADOR', 'REVISADO', 'AUTORIZADO', 'ANULADO']

export default function VoucherList() {
  const navigate = useNavigate()
  const [proyectos, setProyectos] = useState([])
  const [vouchers, setVouchers] = useState([])
  const [filtros, setFiltros] = useState({ proyecto_id: '', estado: '', q: '', desde: '', hasta: '' })
  const [cargando, setCargando] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    api.proyectos().then(setProyectos).catch(() => {})
  }, [])

  useEffect(() => {
    setCargando(true)
    const t = setTimeout(() => {
      api
        .listarVouchers(filtros)
        .then((data) => {
          setVouchers(data)
          setError('')
        })
        .catch((e) => setError(e.message))
        .finally(() => setCargando(false))
    }, 250)
    return () => clearTimeout(t)
  }, [filtros])

  const nombreProyecto = useMemo(() => {
    const map = {}
    for (const p of proyectos) map[p.id] = p.nombre
    return map
  }, [proyectos])

  const set = (campo) => (e) => setFiltros((f) => ({ ...f, [campo]: e.target.value }))

  return (
    <div>
      <div className="mb-5 flex items-center justify-between">
        <h1 className="text-xl font-semibold tracking-tight">Vouchers</h1>
        <button
          onClick={() => navigate('/nuevo')}
          className="rounded-md bg-brand px-3 py-2 text-sm text-white hover:bg-brand-700"
        >
          Nuevo voucher
        </button>
      </div>

      <div className="mb-4 grid grid-cols-1 gap-3 rounded-lg bg-white p-4 ring-1 ring-inset ring-slate-200 sm:grid-cols-5">
        <Campo etiqueta="Proyecto">
          <select value={filtros.proyecto_id} onChange={set('proyecto_id')} className={inputCss}>
            <option value="">Todos</option>
            {proyectos.map((p) => (
              <option key={p.id} value={p.id}>{p.nombre}</option>
            ))}
          </select>
        </Campo>
        <Campo etiqueta="Estado">
          <select value={filtros.estado} onChange={set('estado')} className={inputCss}>
            {ESTADOS.map((e) => (
              <option key={e} value={e}>{e ? e.toLowerCase() : 'Todos'}</option>
            ))}
          </select>
        </Campo>
        <Campo etiqueta="Buscar en concepto">
          <input value={filtros.q} onChange={set('q')} placeholder="texto…" className={inputCss} />
        </Campo>
        <Campo etiqueta="Desde">
          <input type="date" value={filtros.desde} onChange={set('desde')} className={inputCss} />
        </Campo>
        <Campo etiqueta="Hasta">
          <input type="date" value={filtros.hasta} onChange={set('hasta')} className={inputCss} />
        </Campo>
      </div>

      {error && <p className="mb-3 rounded-md bg-rose-50 px-3 py-2 text-sm text-rose-700">{error}</p>}

      <div className="overflow-hidden rounded-lg bg-white ring-1 ring-inset ring-slate-200">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-slate-200 text-left text-xs text-slate-500">
              <th className="px-4 py-2.5 font-medium">Número</th>
              <th className="px-4 py-2.5 font-medium">Fecha</th>
              <th className="px-4 py-2.5 font-medium">Proyecto</th>
              <th className="px-4 py-2.5 font-medium">Concepto</th>
              <th className="px-4 py-2.5 text-right font-medium">Total</th>
              <th className="px-4 py-2.5 font-medium">Estado</th>
            </tr>
          </thead>
          <tbody>
            {!cargando && vouchers.length === 0 && (
              <tr>
                <td colSpan={6} className="px-4 py-10 text-center text-sm text-slate-400">
                  No hay vouchers con estos filtros. Crea el primero con “Nuevo voucher”.
                </td>
              </tr>
            )}
            {vouchers.map((v) => (
              <tr
                key={v.id}
                onClick={() => navigate(`/voucher/${v.id}`)}
                className="cursor-pointer border-b border-slate-100 last:border-0 hover:bg-slate-50"
              >
                <td className="px-4 py-2.5 font-mono text-xs text-brand-700">{v.numero}</td>
                <td className="px-4 py-2.5 text-slate-600">{v.fecha}</td>
                <td className="px-4 py-2.5 text-slate-600">{nombreProyecto[v.proyecto_id] || '—'}</td>
                <td className="max-w-xs truncate px-4 py-2.5 text-slate-700">{v.concepto}</td>
                <td className="px-4 py-2.5 text-right tabular-nums text-ink">{money(v.total)}</td>
                <td className="px-4 py-2.5"><EstadoBadge estado={v.estado} /></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}

const inputCss =
  'w-full rounded-md border border-slate-300 px-2.5 py-1.5 text-sm outline-none focus:border-brand focus:ring-1 focus:ring-brand'

function Campo({ etiqueta, children }) {
  return (
    <label className="block">
      <span className="mb-1 block text-xs text-slate-500">{etiqueta}</span>
      {children}
    </label>
  )
}
