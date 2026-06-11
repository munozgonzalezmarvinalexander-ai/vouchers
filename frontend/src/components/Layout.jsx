import { Link, useLocation } from 'react-router-dom'

export default function Layout({ children }) {
  const { pathname } = useLocation()
  const enLista = pathname === '/'
  return (
    <div className="min-h-screen">
      <header className="border-b border-slate-200 bg-white">
        <div className="mx-auto flex h-14 max-w-5xl items-center justify-between px-5">
          <Link to="/" className="font-semibold tracking-tight text-ink">
            Vouchers <span className="text-brand">contables</span>
          </Link>
          <nav className="flex items-center gap-1 text-sm">
            <Link
              to="/"
              className={`rounded-md px-3 py-1.5 ${
                enLista ? 'bg-brand-50 text-brand-700' : 'text-slate-600 hover:bg-slate-100'
              }`}
            >
              Vouchers
            </Link>
            <Link
              to="/reportes"
              className={`rounded-md px-3 py-1.5 ${
                pathname === '/reportes' ? 'bg-brand-50 text-brand-700' : 'text-slate-600 hover:bg-slate-100'
              }`}
            >
              Reportes
            </Link>
            <Link
              to="/configuracion"
              className={`rounded-md px-3 py-1.5 ${
                pathname === '/configuracion' ? 'bg-brand-50 text-brand-700' : 'text-slate-600 hover:bg-slate-100'
              }`}
            >
              Impresión
            </Link>
            <Link
              to="/nuevo"
              className="rounded-md bg-brand px-3 py-1.5 text-white hover:bg-brand-700"
            >
              Nuevo voucher
            </Link>
          </nav>
        </div>
      </header>
      <main className="mx-auto max-w-5xl px-5 py-7">{children}</main>
    </div>
  )
}
