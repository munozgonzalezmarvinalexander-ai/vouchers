import { useEffect, useState } from 'react'
import { api, previewConfigUrl } from '../api/client.js'

const CAMPOS = [
  { k: 'fuente_pt', label: 'Tamaño de letra', unidad: 'pt', step: 0.5, min: 7, max: 22 },
  { k: 'espacio_concepto_mm', label: 'Espacio entre concepto y partidas', unidad: 'mm', step: 1, min: 0, max: 60 },
  { k: 'espacio_firmas_mm', label: 'Espacio entre partidas y firmas', unidad: 'mm', step: 1, min: 0, max: 80 },
  { k: 'margen_inferior_mm', label: 'Margen inferior (qué tan abajo)', unidad: 'mm', step: 1, min: 0, max: 80 },
  { k: 'margen_lateral_mm', label: 'Márgenes laterales', unidad: 'mm', step: 1, min: 0, max: 50 },
]

const DEFAULTS = {
  fuente_pt: 12,
  espacio_concepto_mm: 14,
  espacio_firmas_mm: 28,
  margen_inferior_mm: 15,
  margen_lateral_mm: 18,
}

const ESCALA = 0.46 // la hoja carta (816×1054 px a 96dpi) se muestra a escala

export default function Configuracion() {
  const [form, setForm] = useState(null)
  const [guardando, setGuardando] = useState(false)
  const [guardado, setGuardado] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    api.getConfiguracion()
      .then((c) => setForm(c))
      .catch(() => setForm({ ...DEFAULTS }))
  }, [])

  if (!form) return <p className="text-slate-400">Cargando…</p>

  const set = (k) => (e) => {
    setGuardado(false)
    setForm((f) => ({ ...f, [k]: e.target.value === '' ? '' : Number(e.target.value) }))
  }

  async function guardar() {
    setGuardando(true)
    setError('')
    try {
      const limpio = Object.fromEntries(
        Object.entries(form).map(([k, v]) => [k, Number(v) || DEFAULTS[k] || 0]),
      )
      await api.guardarConfiguracion(limpio)
      setForm(limpio)
      setGuardado(true)
    } catch (e) {
      setError(e.message)
    } finally {
      setGuardando(false)
    }
  }

  return (
    <div className="space-y-5">
      <div>
        <h1 className="text-xl font-semibold tracking-tight">Configuración de impresión</h1>
        <p className="mt-1 text-sm text-slate-500">
          Ajusta el tamaño y los espacios. La vista previa se actualiza al instante; cuando te guste, presiona Guardar.
          Lo que guardes aplica a todas las computadoras.
        </p>
      </div>

      <div className="grid gap-6 md:grid-cols-[minmax(0,1fr)_auto]">
        {/* Controles */}
        <div className="space-y-4">
          {CAMPOS.map((c) => (
            <label key={c.k} className="block">
              <span className="mb-1 flex items-center justify-between text-sm text-slate-600">
                <span>{c.label}</span>
                <span className="font-mono text-xs text-slate-400">{c.unidad}</span>
              </span>
              <input
                type="number"
                value={form[c.k]}
                onChange={set(c.k)}
                step={c.step}
                min={c.min}
                max={c.max}
                className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:border-brand focus:outline-none"
              />
            </label>
          ))}

          <div className="flex items-center gap-3 pt-1">
            <button
              onClick={guardar}
              disabled={guardando}
              className="rounded-md bg-brand px-4 py-2 text-sm font-medium text-white hover:bg-brand-700 disabled:opacity-50"
            >
              {guardando ? 'Guardando…' : 'Guardar ajustes'}
            </button>
            <button
              onClick={() => { setForm({ ...DEFAULTS }); setGuardado(false) }}
              className="rounded-md px-3 py-2 text-sm text-slate-500 hover:bg-slate-100"
            >
              Restaurar valores
            </button>
            {guardado && <span className="text-sm text-emerald-600">Guardado ✓</span>}
            {error && <span className="text-sm text-red-600">{error}</span>}
          </div>
        </div>

        {/* Vista previa (hoja carta a escala) */}
        <div>
          <p className="mb-2 text-xs uppercase tracking-wide text-slate-400">Vista previa — hoja carta</p>
          <div
            className="overflow-hidden rounded-md border border-slate-300 shadow-sm"
            style={{ width: 816 * ESCALA, height: 1054 * ESCALA }}
          >
            <iframe
              title="vista-previa"
              src={previewConfigUrl(form)}
              style={{
                width: 816,
                height: 1054,
                border: 0,
                transform: `scale(${ESCALA})`,
                transformOrigin: 'top left',
                background: '#fff',
              }}
            />
          </div>
          <p className="mt-2 max-w-[380px] text-xs text-slate-400">
            La parte de arriba queda en blanco a propósito: ahí va el comprobante del banco. El voucher se ancla abajo.
          </p>
        </div>
      </div>
    </div>
  )
}
