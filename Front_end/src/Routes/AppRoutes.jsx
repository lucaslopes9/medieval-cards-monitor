import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Login from '../pages/login/login.jsx'
import Register from '../pages/Register/Register.jsx'
import Dashboard from '../pages/painel_adm/Dashboard.jsx'

function AppRoutes() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Login />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/dashboard" element={<Dashboard />} />
      </Routes>
    </BrowserRouter>
  )
}

export default AppRoutes