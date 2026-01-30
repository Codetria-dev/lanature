import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider, useAuth } from './contexts/AuthContext'
import IntroPage from './pages/IntroPage'
import LandingPage from './pages/LandingPage'
import Login from './pages/Login'
import Register from './pages/Register'
import Dashboard from './pages/Dashboard'
import Pets from './pages/Pets'
import Routines from './pages/Routines'
import History from './pages/History'
import Admin from './pages/Admin'
import Contact from './pages/Contact'
import Layout from './components/Layout'
import AdminLayout from './components/AdminLayout'
import ProtectedRoute from './components/ProtectedRoute'
import { t } from './i18n'

function PublicRoute({ children }) {
  const { user, loading } = useAuth()
  
  if (loading) {
    return <div className="flex items-center justify-center min-h-screen">{t('loading')}</div>
  }
  
  if (user) {
    // Se for superuser, redireciona para admin, senão para dashboard
    return <Navigate to={user.is_superuser ? "/admin" : "/dashboard"} replace />
  }
  
  return children
}

function App() {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          <Route path="/" element={<IntroPage />} />
          <Route path="/intro" element={<IntroPage />} />
          <Route path="/home" element={<LandingPage />} />
          <Route path="/login" element={<PublicRoute><Login /></PublicRoute>} />
          <Route path="/register" element={<PublicRoute><Register /></PublicRoute>} />
          
          {/* Rotas protegidas - requerem usuário logado */}
          <Route 
            path="/dashboard" 
            element={
              <ProtectedRoute>
                <Layout><Dashboard /></Layout>
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/pets" 
            element={
              <ProtectedRoute>
                <Layout><Pets /></Layout>
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/routines" 
            element={
              <ProtectedRoute>
                <Layout><Routines /></Layout>
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/history" 
            element={
              <ProtectedRoute>
                <Layout><History /></Layout>
              </ProtectedRoute>
            } 
          />
          
          {/* Rota admin - requer role admin */}
          <Route 
            path="/admin" 
            element={
              <ProtectedRoute requiredRole="admin" redirectTo="/dashboard">
                <AdminLayout><Admin /></AdminLayout>
              </ProtectedRoute>
            } 
          />
          
          <Route path="/contact" element={<Layout><Contact /></Layout>} />
        </Routes>
      </Router>
    </AuthProvider>
  )
}

export default App
