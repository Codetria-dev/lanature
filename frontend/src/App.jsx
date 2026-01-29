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
import { t } from './i18n'

function PrivateRoute({ children }) {
  const { user, loading } = useAuth()
  
  if (loading) {
    return <div className="flex items-center justify-center min-h-screen">{t('loading')}</div>
  }
  
  return user ? children : <Navigate to="/login" />
}

function UserRoute({ children }) {
  const { user, loading } = useAuth()
  
  if (loading) {
    return <div className="flex items-center justify-center min-h-screen">{t('loading')}</div>
  }
  
  if (!user) {
    return <Navigate to="/login" />
  }
  
  // Se for superuser, redireciona para admin
  if (user.is_superuser === true) {
    return <Navigate to="/admin" replace />
  }
  
  return children
}

function AdminRoute({ children }) {
  const { user, loading } = useAuth()
  
  if (loading) {
    return <div className="flex items-center justify-center min-h-screen">{t('loading')}</div>
  }
  
  if (!user) {
    return <Navigate to="/login" />
  }
  
  // Se não for superuser, redireciona para dashboard
  if (user.is_superuser !== true) {
    return <Navigate to="/dashboard" replace />
  }
  
  return children
}

function PublicRoute({ children }) {
  const { user, loading } = useAuth()
  
  if (loading) {
    return <div className="flex items-center justify-center min-h-screen">{t('loading')}</div>
  }
  
  if (user) {
    // Se for superuser, redireciona para admin, senão para dashboard
    return <Navigate to={user.is_superuser ? "/admin" : "/dashboard"} />
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
          <Route path="/dashboard" element={<UserRoute><Layout><Dashboard /></Layout></UserRoute>} />
          <Route path="/pets" element={<UserRoute><Layout><Pets /></Layout></UserRoute>} />
          <Route path="/routines" element={<UserRoute><Layout><Routines /></Layout></UserRoute>} />
          <Route path="/history" element={<UserRoute><Layout><History /></Layout></UserRoute>} />
          <Route path="/admin" element={<AdminRoute><AdminLayout><Admin /></AdminLayout></AdminRoute>} />
          <Route path="/contact" element={<Layout><Contact /></Layout>} />
        </Routes>
      </Router>
    </AuthProvider>
  )
}

export default App
