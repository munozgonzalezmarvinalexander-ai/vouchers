const ESTILOS = {
  BORRADOR: 'bg-amber-50 text-amber-700 ring-amber-200',
  REVISADO: 'bg-sky-50 text-sky-700 ring-sky-200',
  AUTORIZADO: 'bg-emerald-50 text-emerald-700 ring-emerald-200',
  ANULADO: 'bg-slate-100 text-slate-500 ring-slate-200',
}

export default function EstadoBadge({ estado }) {
  return (
    <span
      className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium capitalize ring-1 ring-inset ${
        ESTILOS[estado] || ESTILOS.BORRADOR
      }`}
    >
      {estado?.toLowerCase()}
    </span>
  )
}
