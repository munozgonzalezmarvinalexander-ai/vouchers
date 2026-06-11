import { useEffect, useState } from 'react'
import { api, libroExcelUrl } from '../api/client.js'
import { money } from '../lib/format.js'

export default function Reportes() {
  const [proyectos, setProyectos] = useState([])
  const [filtros, setFiltros] = useState({ proyecto_id: '', desde: '', hasta: '' })
  const [libro, setLibro] = useState(null)
  const [partidas, setPartidas] = useState([])
  const [error, setError] = useState('')
  const [cargando, setCargando] = useState(false)

  useEffect(() => {
    api.proyectos().then(setProyectos).catch(() => {})
  }, [])

  useEffect(() => {
    let vivo = true
    setCargando(true)
    setError('')
    Promise.all([api.libroVouchers(filtros), api.totalesPorPartida(filtros)])
      .then(([lb, pt]) => {
        if (!vivo) return
        setLibro(lb)
        setPartidas(pt)
      })
      .catch((e) => vivo && setError(e.message))
      .finally(() => vivo && setCargando(false))
    return () => {
      vivo = false
    }
  }, [filtros])

  const set = (campo) => (e) => setFiltros((f) => ({ ...f, [campo]: e.target.value }))

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-semibold tracking-tight">Reportes</h1>
        <a
          href={libroExcelUrl(filtros)}
          className="rounded-md border border-slate-300 px-3 py-1.5 text-sm text-slate-700 hover:bg-slate-100"
        >
          Descargar libro (Excel)
        </a>
      </div>

      <div className="flex flex-wrap items-end gap-3 rounded-lg border border-slate-200 bg-white p-4">
        <label className="text-sm">
          <span className="mb-1 block text-slate-500">Proyecto</span>
          <select value={filtros.proyecto_id} onChange={set('proyecto_id')} className="rounded-md border border-slate-300 px-2 py-1.5">
            <option value="">Todos</option>
            {proyectos.map((p) => (
              <option key={p.id} value={p.id}>{p.nombre}</option>
            ))}
          </select>
        </label>
        <label className="text-sm">
          <span className="mb-1 block text-slate-500">Desde</span>
          <input type="date" value={filtros.desde} onChange={set('desde')} className="rounded-md border border-slate-300 px-2 py-1.5" />
        </label>
        <label className="text-sm">
          <span className="mb-1 block text-slate-500">Hasta</span>
          <input type="date" value={filtros.hasta} onChange={set('hasta')} className="rounded-md border border-slate-300 px-2 py-1.5" />
        </label>
        {cargando && <span className="text-sm text-slate-400">Cargando…</span>}
      </div>

      {error && <p className="rounded-md bg-red-50 px-3 py-2 text-sm text-red-700">{error}</p>}

      {/* Libro de vouchers */}
      <section className="rounded-lg border border-slate-200 bg-white">
        <div className="flex items-center justify-between border-b border-slate-200 px-4 py-3">
          <h2 className="font-medium">Libro de vouchers</h2>
          {libro && (
            <span className="text-sm text-slate-500">
              {libro.conteo} vouchers · total <span className="font-semibold text-ink">{money(Number(libro.total))}</span>
            </span>
          )}
        </div>
        <table className="w-full text-sm">
          <thead>
            <tr className="text-left text-xs uppercase tracking-wide text-slate-400">
              <th className="px-4 py-2">Número</th>
              <th className="px-4 py-2">Fecha</th>
              <th className="px-4 py-2">Concepto</th>
              <th className="px-4 py-2 text-right">Total</th>
              <th className="px-4 py-2">Estado</th>
            </tr>
          </thead>
          <tbody>
            {libro?.vouchers?.length ? (
              libro.vouchers.map((v) => (
                <tr key={v.id} className="border-t border-slate-100">
                  <td className="px-4 py-2 font-mono text-xs text-brand-700">{v.numero}</td>
                  <td className="px-4 py-2 whitespace-nowrap">{v.fecha}</td>
                  <td className="px-4 py-2">{v.concepto}</td>
                  <td className="px-4 py-2 text-right tabular-nums">{money(Number(v.total))}</td>
                  <td className="px-4 py-2 capitalize text-slate-500">{v.estado?.toLowerCase()}</td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan={5} className="px-4 py-6 text-center text-slate-400">Sin vouchers en este filtro.</td>
              </tr>
            )}
          </tbody>
        </table>
      </section>

      {/* Totales por partida */}
      <section className="rounded-lg border border-slate-200 bg-white">
        <div className="border-b border-slate-200 px-4 py-3">
          <h2 className="font-medium">Totales por partida (gasto)</h2>
        </div>
        <table className="w-full text-sm">
          <thead>
            <tr className="text-left text-xs uppercase tracking-wide text-slate-400">
              <th className="px-4 py-2">Código</th>
              <th className="px-4 py-2">Cuenta</th>
              <th className="px-4 py-2 text-right">Total</th>
              <th className="px-4 py-2 text-right">Veces</th>
            </tr>
          </thead>
          <tbody>
            {partidas.length ? (
              partidas.map((p) => (
                <tr key={p.codigo} className="border-t border-slate-100">
                  <td className="px-4 py-2 font-mono text-xs text-slate-600">{p.codigo}</td>
                  <td className="px-4 py-2">{p.nombre}</td>
                  <td className="px-4 py-2 text-right tabular-nums">{money(Number(p.total))}</td>
                  <td className="px-4 py-2 text-right text-slate-500">{p.veces}</td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan={4} className="px-4 py-6 text-center text-slate-400">Sin movimientos en este filtro.</td>
              </tr>
            )}
          </tbody>
        </table>
      </section>
    </div>
  )
}
