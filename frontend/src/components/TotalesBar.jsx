import { money } from '../lib/format.js'

// El elemento distintivo del producto: muestra debe, haber y el cuadre en vivo.
export default function TotalesBar({ totalDebe, totalHaber }) {
  const diferencia = Math.round((totalDebe - totalHaber) * 100) / 100
  const cuadrado = Math.abs(diferencia) < 0.005
  return (
    <div className="grid grid-cols-3 gap-3">
      <Caja titulo="Total debe" valor={money(totalDebe)} />
      <Caja titulo="Total haber" valor={money(totalHaber)} />
      <div
        className={`rounded-lg px-4 py-3 ring-1 ring-inset ${
          cuadrado ? 'bg-emerald-50 ring-emerald-200' : 'bg-rose-50 ring-rose-200'
        }`}
      >
        <div className={`text-xs ${cuadrado ? 'text-emerald-700' : 'text-rose-700'}`}>
          {cuadrado ? 'Cuadre' : 'Descuadre'}
        </div>
        <div
          className={`text-lg font-semibold tabular-nums ${
            cuadrado ? 'text-emerald-700' : 'text-rose-700'
          }`}
        >
          {cuadrado ? 'Cuadrado' : money(Math.abs(diferencia))}
        </div>
      </div>
    </div>
  )
}

function Caja({ titulo, valor }) {
  return (
    <div className="rounded-lg bg-white px-4 py-3 ring-1 ring-inset ring-slate-200">
      <div className="text-xs text-slate-500">{titulo}</div>
      <div className="text-lg font-semibold tabular-nums text-ink">{valor}</div>
    </div>
  )
}
