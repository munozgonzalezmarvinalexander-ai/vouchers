import { Routes, Route, Navigate } from 'react-router-dom'
import Layout from './components/Layout.jsx'
import VoucherList from './pages/VoucherList.jsx'
import VoucherForm from './pages/VoucherForm.jsx'
import Reportes from './pages/Reportes.jsx'
import Configuracion from './pages/Configuracion.jsx'

export default function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<VoucherList />} />
        <Route path="/nuevo" element={<VoucherForm />} />
        <Route path="/voucher/:id" element={<VoucherForm />} />
        <Route path="/reportes" element={<Reportes />} />
        <Route path="/configuracion" element={<Configuracion />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Layout>
  )
}
