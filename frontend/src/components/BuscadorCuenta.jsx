import { useEffect, useRef, useState } from 'react'
import { api } from '../api/client.js'

// Busca cuentas en el catálogo conforme se escribe (con un pequeño retardo
// para no consultar en cada tecla) y deja elegir una.
export default function BuscadorCuenta({ onSelect, disabled }) {
  const [q, setQ] = useState('')
  const [resultados, setResultados] = useState([])
  const [abierto, setAbierto] = useState(false)
  const caja = useRef(null)

  useEffect(() => {
    if (!q.trim()) {
      setResultados([])
      return
    }
    const t = setTimeout(async () => {
      try {
        setResultados(await api.cuentas(q))
      } catch {
        setResultados([])
      }
    }, 250)
    return () => clearTimeout(t)
  }, [q])

  useEffect(() => {
    const fuera = (e) => {
      if (caja.current && !caja.current.contains(e.target)) setAbierto(false)
    }
    document.addEventListener('mousedown', fuera)
    return () => document.removeEventListener('mousedown', fuera)
  }, [])

  return (
    <div className="relative" ref={caja}>
      <input
        value={q}
        disabled={disabled}
        onChange={(e) => {
          setQ(e.target.value)
          setAbierto(true)
        }}
        onFocus={() => setAbierto(true)}
        placeholder="Buscar cuenta por código o nombre…"
        className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm outline-none focus:border-brand focus:ring-1 focus:ring-brand disabled:bg-slate-100"
      />
      {abierto && resultados.length > 0 && (
        <ul className="absolute z-20 mt-1 max-h-64 w-full overflow-auto rounded-md border border-slate-200 bg-white shadow-lg">
          {resultados.slice(0, 20).map((c) => (
            <li key={c.id}>
              <button
                type="button"
                onClick={() => {
                  onSelect(c)
                  setQ('')
                  setResultados([])
                  setAbierto(false)
                }}
                className="flex w-full items-center gap-3 px-3 py-2 text-left text-sm hover:bg-brand-50"
              >
                <span className="font-mono text-xs text-brand-700">{c.codigo}</span>
                <span className="truncate text-slate-700">{c.nombre}</span>
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}
