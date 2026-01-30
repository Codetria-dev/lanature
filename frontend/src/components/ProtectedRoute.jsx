import { Navigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { t } from '../i18n'

/**
 * ProtectedRoute - Componente para proteger rotas que requerem autenticação
 * 
 * Verifica:
 * 1. Usuário está logado
 * 2. Token válido (verificado via AuthContext)
 * 3. Role específica (se requiredRole for fornecido)
 * 
 * @param {Object} props
 * @param {React.ReactNode} props.children - Componente a ser renderizado se autorizado
 * @param {string} [props.requiredRole] - Role requerida ('admin' ou undefined para qualquer usuário logado)
 * @param {string} [props.redirectTo] - Rota para redirecionar se não autorizado (padrão: '/login' ou '/dashboard')
 */
export default function ProtectedRoute({ children, requiredRole, redirectTo }) {
  const { user, loading } = useAuth()

  // Mostra loading enquanto verifica autenticação
  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-600 mx-auto mb-4"></div>
          <p className="text-gray-600">{t('loading')}</p>
        </div>
      </div>
    )
  }

  // 1. Verifica se usuário está logado
  if (!user) {
    return <Navigate to="/login" replace />
  }

  // 2. Verifica role específica (se necessário)
  if (requiredRole === 'admin') {
    // Verifica se é admin (is_superuser === true)
    if (user.is_superuser !== true) {
      // Não é admin → redireciona para dashboard
      return <Navigate to={redirectTo || '/dashboard'} replace />
    }
  }

  // 3. Usuário autorizado → renderiza children
  return children
}
