import { useEffect, useMemo, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { api, docUrls } from '../api/client.js'
import { hoy } from '../lib/format.js'
import TotalesBar from '../components/TotalesBar.jsx'
import BuscadorCuenta from '../components/BuscadorCuenta.jsx'
import FavoritosChips from '../components/FavoritosChips.jsx'
import EstadoBadge from '../components/EstadoBadge.jsx'

const nuevaLinea = (cuenta) => ({
  key: crypto.randomUUID(),
  cuenta,
  descripcion: cuenta.nombre,
  debe: '',
  haber: '',
})

export default function VoucherForm() {
  const { id } = useParams()
  const editando = Boolean(id)
  const navigate = useNavigate()

  const [proyectos, setProyectos] = useState([])
  const [firmantes, setFirmantes] = useState([])
  const [favoritas, setFavoritas] = useState([])

  const [proyectoId, setProyectoId] = useState('')
  const [fecha, setFecha] = useState(hoy())
  const [concepto, setConcepto] = useState('')
  const [firmas, setFirmas] = useState({ elaborado_por_id: '', revisado_por_id: '', autorizado_por_id: '' })
  const [lineas, setLineas] = useState([])

  const [numero, setNumero] = useState(null)
  const [estado, setEstado] = useState('BORRADOR')
  const [cargando, setCargando] = useState(editando)
  const [guardando, setGuardando] = useState(false)
  const [error, setError] = useState('')
  const [orto, setOrto] = useState(null) // null = sin revisar, [] = ok, [...] = observaciones
  const [revisandoOrto, setRevisandoOrto] = useState(false)
  const [historial, setHistorial] = useState([])

  const soloLectura = editando && estado !== 'BORRADOR'

  // Catálogos base.
  useEffect(() => {
    api.proyectos().then(setProyectos).catch(() => {})
    api.firmantes().then((f) => {
      setFirmantes(f)
      if (!editando) {
        const primero = (rol) => f.find((x) => x.rol_firma === rol)?.id || ''
        setFirmas({
          elaborado_por_id: primero('ELABORA'),
          revisado_por_id: primero('REVISA'),
          autorizado_por_id: primero('AUTORIZA'),
        })
      }
    }).catch(() => {})
  }, [editando])

  // Si estamos editando, cargar el voucher.
  useEffect(() => {
    if (!editando) return
    setCargando(true)
    api.obtenerVoucher(id)
      .then((v) => {
        setProyectoId(String(v.proyecto_id))
        setFecha(v.fecha)
        setConcepto(v.concepto)
        setNumero(v.numero)
        setEstado(v.estado)
        setFirmas({
          elaborado_por_id: v.elaborado_por?.id || '',
          revisado_por_id: v.revisado_por?.id || '',
          autorizado_por_id: v.autorizado_por?.id || '',
        })
        setLineas(
          v.detalles.map((d) => ({
            key: crypto.randomUUID(),
            cuenta: d.cuenta,
            descripcion: d.descripcion,
            debe: Number(d.debe) ? String(d.debe) : '',
            haber: Number(d.haber) ? String(d.haber) : '',
          }))
        )
      })
      .catch((e) => setError(e.message))
      .finally(() => setCargando(false))
  }, [id, editando])

  // Favoritas del proyecto seleccionado (se alimentan por uso).
  useEffect(() => {
    if (!proyectoId) return setFavoritas([])
    api.favoritas(proyectoId).then(setFavoritas).catch(() => setFavoritas([]))
  }, [proyectoId])

  // Historial / auditoría del voucher (se recarga cuando cambia de estado).
  useEffect(() => {
    if (!editando) return
    api.auditoria(id).then(setHistorial).catch(() => setHistorial([]))
  }, [id, editando, estado])

  const { totalDebe, totalHaber } = useMemo(() => {
    let d = 0, h = 0
    for (const l of lineas) {
      d += parseFloat(l.debe) || 0
      h += parseFloat(l.haber) || 0
    }
    return { totalDebe: d, totalHaber: h }
  }, [lineas])

  const cuadrado = Math.abs(Math.round((totalDebe - totalHaber) * 100) / 100) < 0.005

  const agregarCuenta = (cuenta) => setLineas((ls) => [...ls, nuevaLinea(cuenta)])
  const quitarLinea = (key) => setLineas((ls) => ls.filter((l) => l.key !== key))
  const editarLinea = (key, campo, valor) =>
    setLineas((ls) => ls.map((l) => (l.key === key ? { ...l, [campo]: valor } : l)))

  function payload(estadoDestino) {
    return {
      proyecto_id: Number(proyectoId),
      fecha,
      concepto,
      estado: estadoDestino,
      elaborado_por_id: firmas.elaborado_por_id || null,
      revisado_por_id: firmas.revisado_por_id || null,
      autorizado_por_id: firmas.autorizado_por_id || null,
      detalles: lineas.map((l, i) => ({
        cuenta_id: l.cuenta.id,
        descripcion: l.descripcion,
        debe: l.debe || '0',
        haber: l.haber || '0',
        orden: i,
      })),
    }
  }

  async function guardar(estadoDestino) {
    setError('')
    setGuardando(true)
    try {
      if (!editando) {
        const v = await api.crearVoucher(payload(estadoDestino))
        navigate(`/voucher/${v.id}`)
      } else {
        await api.actualizarVoucher(id, payload(estadoDestino))
        if (estadoDestino === 'REVISADO') await api.cambiarEstado(id, 'REVISADO')
        const v = await api.obtenerVoucher(id)
        setEstado(v.estado)
      }
    } catch (e) {
      setError(e.message)
    } finally {
      setGuardando(false)
    }
  }

  async function transicionar(destino) {
    setError('')
    setGuardando(true)
    try {
      await api.cambiarEstado(id, destino)
      const v = await api.obtenerVoucher(id)
      setEstado(v.estado)
    } catch (e) {
      setError(e.message)
    } finally {
      setGuardando(false)
    }
  }

  async function revisarOrtografia() {
    setRevisandoOrto(true)
    try {
      // Revisa el concepto y las descripciones de las líneas (texto libre).
      const texto = [concepto, ...lineas.map((l) => l.descripcion)].join(' ')
      const { palabras } = await api.revisarOrtografia(texto)
      setOrto(palabras)
    } catch {
      setOrto(null)
    } finally {
      setRevisandoOrto(false)
    }
  }

  if (cargando) return <p className="text-sm text-slate-500">Cargando…</p>

  return (
    <div className="space-y-5">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-semibold tracking-tight">
          {editando ? 'Voucher' : 'Nuevo voucher'}
          {numero && <span className="ml-2 font-mono text-sm text-brand-700">{numero}</span>}
        </h1>
        {editando && <EstadoBadge estado={estado} />}
      </div>

      {editando && (
        <div className="flex flex-wrap gap-2">
          <a
            href={docUrls(id).imprimir}
            target="_blank"
            rel="noreferrer"
            className="rounded-md border border-brand px-3 py-1.5 text-sm text-brand-700 hover:bg-brand-50"
          >
            Imprimir
          </a>
          <a
            href={docUrls(id).pdf}
            className="rounded-md border border-slate-300 px-3 py-1.5 text-sm text-slate-700 hover:bg-slate-100"
          >
            Descargar PDF
          </a>
          <a
            href={docUrls(id).excel}
            className="rounded-md border border-slate-300 px-3 py-1.5 text-sm text-slate-700 hover:bg-slate-100"
          >
            Exportar Excel
          </a>
          <a
            href={docUrls(id).vistaPrevia}
            target="_blank"
            rel="noreferrer"
            className="rounded-md px-3 py-1.5 text-sm text-slate-500 hover:bg-slate-100"
          >
            Vista previa
          </a>
        </div>
      )}

      {error && <p className="rounded-md bg-rose-50 px-3 py-2 text-sm text-rose-700">{error}</p>}

      {/* Encabezado */}
      <div className="grid grid-cols-1 gap-3 sm:grid-cols-3">
        <label className="block">
          <span className="mb-1 block text-xs text-slate-500">Proyecto / fondo</span>
          <select
            value={proyectoId}
            disabled={soloLectura}
            onChange={(e) => setProyectoId(e.target.value)}
            className={inputCss}
          >
            <option value="">Selecciona…</option>
            {proyectos.map((p) => (
              <option key={p.id} value={p.id}>{p.nombre}</option>
            ))}
          </select>
        </label>
        <label className="block">
          <span className="mb-1 block text-xs text-slate-500">Fecha</span>
          <input type="date" value={fecha} disabled={soloLectura} onChange={(e) => setFecha(e.target.value)} className={inputCss} />
        </label>
      </div>

      <label className="block">
        <span className="mb-1 block text-xs text-slate-500">Concepto</span>
        <textarea
          value={concepto}
          disabled={soloLectura}
          onChange={(e) => setConcepto(e.target.value)}
          lang="es"
          spellCheck
          rows={2}
          className={`${inputCss} resize-y`}
          placeholder="Describe el gasto…"
        />
      </label>

      <div className="-mt-2">
        <button
          type="button"
          onClick={revisarOrtografia}
          disabled={revisandoOrto || !concepto}
          className="text-sm text-brand-700 hover:underline disabled:opacity-50"
        >
          {revisandoOrto ? 'Revisando…' : 'Revisar ortografía'}
        </button>
        {orto !== null && orto.length === 0 && (
          <span className="ml-2 text-sm text-emerald-600">Sin observaciones.</span>
        )}
        {orto !== null && orto.length > 0 && (
          <div className="mt-2 rounded-md bg-amber-50 px-3 py-2 text-sm text-amber-800">
            <span className="font-medium">Posibles errores:</span>{' '}
            {orto.map((p, i) => (
              <span key={p.palabra + i}>
                <span className="font-medium">{p.palabra}</span>
                {p.sugerencias.length > 0 && <> → {p.sugerencias.join(', ')}</>}
                {i < orto.length - 1 ? ' · ' : ''}
              </span>
            ))}
          </div>
        )}
      </div>

      {/* Agregar cuentas */}
      {!soloLectura && (
        <div className="space-y-2">
          <span className="block text-xs text-slate-500">Agregar líneas</span>
          <BuscadorCuenta onSelect={agregarCuenta} />
          {proyectoId && <FavoritosChips favoritas={favoritas} onAdd={agregarCuenta} />}
        </div>
      )}

      {/* Líneas */}
      <div className="overflow-hidden rounded-lg bg-white ring-1 ring-inset ring-slate-200">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-slate-200 text-left text-xs text-slate-500">
              <th className="px-3 py-2 font-medium">Código</th>
              <th className="px-3 py-2 font-medium">Cuenta / descripción</th>
              <th className="px-3 py-2 text-right font-medium">Debe</th>
              <th className="px-3 py-2 text-right font-medium">Haber</th>
              <th className="w-8" />
            </tr>
          </thead>
          <tbody>
            {lineas.length === 0 && (
              <tr>
                <td colSpan={5} className="px-3 py-8 text-center text-sm text-slate-400">
                  Agrega líneas con el buscador o las favoritas de arriba.
                </td>
              </tr>
            )}
            {lineas.map((l) => (
              <tr key={l.key} className="border-b border-slate-100 last:border-0">
                <td className="px-3 py-2 align-top font-mono text-xs text-brand-700">{l.cuenta.codigo}</td>
                <td className="px-3 py-2">
                  <input
                    value={l.descripcion}
                    disabled={soloLectura}
                    onChange={(e) => editarLinea(l.key, 'descripcion', e.target.value)}
                    className="w-full rounded border border-transparent px-1.5 py-1 hover:border-slate-200 focus:border-brand focus:outline-none focus:ring-1 focus:ring-brand disabled:bg-transparent"
                  />
                </td>
                <td className="px-3 py-2">
                  <input
                    inputMode="decimal"
                    value={l.debe}
                    disabled={soloLectura}
                    onChange={(e) => editarLinea(l.key, 'debe', e.target.value)}
                    className={montoCss}
                  />
                </td>
                <td className="px-3 py-2">
                  <input
                    inputMode="decimal"
                    value={l.haber}
                    disabled={soloLectura}
                    onChange={(e) => editarLinea(l.key, 'haber', e.target.value)}
                    className={montoCss}
                  />
                </td>
                <td className="px-2 py-2 text-center align-middle">
                  {!soloLectura && (
                    <button
                      type="button"
                      onClick={() => quitarLinea(l.key)}
                      className="text-slate-400 hover:text-rose-600"
                      aria-label="Quitar línea"
                    >
                      ✕
                    </button>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <TotalesBar totalDebe={totalDebe} totalHaber={totalHaber} />

      {/* Firmas */}
      <div className="grid grid-cols-1 gap-3 sm:grid-cols-3">
        <SelectFirmante etiqueta="Elaborado por" rol="ELABORA" firmantes={firmantes}
          valor={firmas.elaborado_por_id} disabled={soloLectura}
          onChange={(v) => setFirmas((f) => ({ ...f, elaborado_por_id: v }))} />
        <SelectFirmante etiqueta="Revisado por" rol="REVISA" firmantes={firmantes}
          valor={firmas.revisado_por_id} disabled={soloLectura}
          onChange={(v) => setFirmas((f) => ({ ...f, revisado_por_id: v }))} />
        <SelectFirmante etiqueta="Autorizado por" rol="AUTORIZA" firmantes={firmantes}
          valor={firmas.autorizado_por_id} disabled={soloLectura}
          onChange={(v) => setFirmas((f) => ({ ...f, autorizado_por_id: v }))} />
      </div>

      {/* Acciones */}
      <div className="flex flex-wrap gap-2 border-t border-slate-200 pt-4">
        {(!editando || estado === 'BORRADOR') && (
          <>
            <button onClick={() => guardar('BORRADOR')} disabled={guardando}
              className="rounded-md border border-brand px-4 py-2 text-sm text-brand-700 hover:bg-brand-50 disabled:opacity-50">
              Guardar borrador
            </button>
            <button onClick={() => guardar('REVISADO')} disabled={guardando || !cuadrado}
              title={!cuadrado ? 'El voucher debe cuadrar para revisarlo' : ''}
              className="rounded-md bg-brand px-4 py-2 text-sm text-white hover:bg-brand-700 disabled:opacity-50">
              Guardar y revisar
            </button>
          </>
        )}
        {editando && estado === 'REVISADO' && (
          <>
            <button onClick={() => transicionar('AUTORIZADO')} disabled={guardando}
              className="rounded-md bg-emerald-600 px-4 py-2 text-sm text-white hover:bg-emerald-700 disabled:opacity-50">
              Autorizar
            </button>
            <button onClick={() => transicionar('BORRADOR')} disabled={guardando}
              className="rounded-md border border-slate-300 px-4 py-2 text-sm text-slate-700 hover:bg-slate-100 disabled:opacity-50">
              Devolver a borrador
            </button>
          </>
        )}
        {editando && (estado === 'REVISADO' || estado === 'AUTORIZADO') && (
          <button onClick={() => transicionar('ANULADO')} disabled={guardando}
            className="rounded-md border border-rose-200 px-4 py-2 text-sm text-rose-700 hover:bg-rose-50 disabled:opacity-50">
            Anular
          </button>
        )}
        <button onClick={() => navigate('/')} className="ml-auto rounded-md px-4 py-2 text-sm text-slate-500 hover:bg-slate-100">
          Volver
        </button>
      </div>

      {editando && historial.length > 0 && (
        <div className="rounded-lg border border-slate-200 bg-white p-4">
          <h2 className="mb-2 text-sm font-medium text-slate-700">Historial</h2>
          <ul className="space-y-1 text-sm">
            {historial.map((a) => (
              <li key={a.id} className="flex items-center justify-between text-slate-600">
                <span>
                  <span className="font-medium capitalize text-ink">{a.accion.toLowerCase()}</span> · {a.usuario}
                </span>
                <span className="text-xs text-slate-400">
                  {new Date(a.fecha).toLocaleString('es-GT')}
                </span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  )
}

const inputCss =
  'w-full rounded-md border border-slate-300 px-3 py-2 text-sm outline-none focus:border-brand focus:ring-1 focus:ring-brand disabled:bg-slate-100'
const montoCss =
  'w-28 rounded border border-slate-300 px-2 py-1 text-right tabular-nums outline-none focus:border-brand focus:ring-1 focus:ring-brand disabled:bg-transparent disabled:border-transparent'

function SelectFirmante({ etiqueta, rol, firmantes, valor, disabled, onChange }) {
  const opciones = firmantes.filter((f) => f.rol_firma === rol)
  return (
    <label className="block">
      <span className="mb-1 block text-xs text-slate-500">{etiqueta}</span>
      <select value={valor} disabled={disabled} onChange={(e) => onChange(e.target.value)} className={inputCss}>
        <option value="">—</option>
        {opciones.map((f) => (
          <option key={f.id} value={f.id}>{f.nombre}</option>
        ))}
      </select>
    </label>
  )
}
