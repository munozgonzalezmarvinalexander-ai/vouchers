// Atajos a las cuentas más usadas del proyecto (favoritos automáticos).
export default function FavoritosChips({ favoritas, onAdd }) {
  if (!favoritas.length) {
    return (
      <p className="text-xs text-slate-400">
        Aún no hay favoritas para este proyecto. Se irán mostrando las cuentas que más uses.
      </p>
    )
  }
  return (
    <div className="flex flex-wrap gap-2">
      {favoritas.map((c) => (
        <button
          key={c.id}
          type="button"
          onClick={() => onAdd(c)}
          title={`${c.codigo} · usada ${c.usos} ${c.usos === 1 ? 'vez' : 'veces'}`}
          className="inline-flex items-center gap-1.5 rounded-full border border-slate-200 bg-white px-3 py-1 text-xs text-slate-700 hover:border-brand hover:bg-brand-50"
        >
          <span className="text-brand">+</span>
          {c.nombre}
        </button>
      ))}
    </div>
  )
}
