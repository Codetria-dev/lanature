import { Navigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { t } from '../i18n'

/**
 * ProtectedRoute - Component to protect routes that require authentication
 *
 * Checks:
 * 1. User is logged in
 * 2. Valid token (verified via AuthContext)
 * 3. Required role (if requiredRole is specified)
 *
 * @param {Object} props
 * @param {React.ReactNode} props.children - Component to render if authorized
 * @param {string} [props.requiredRole] - Required role ('admin' or undefined for any logged-in user)
 * @param {string} [props.redirectTo] - Route to redirect if not authorized (default: '/login' or '/dashboard')
 */
export default function ProtectedRoute({ children, requiredRole, redirectTo }) {
  const { user, loading } = useAuth()

  // Shows loading while checking authentication
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

  // 1. Check if user is logged in
  if (!user) {
    return <Navigate to="/login" replace />
  }

  // 2. Check required role (if specified)
  if (requiredRole === 'admin') {
    // Check if user is admin (is_superuser === true)
    if (user.is_superuser !== true) {
      // Not admin → redirect to dashboard
      return <Navigate to={redirectTo || '/dashboard'} replace />
    }
  }

  // 3. User authorized → render children
  return children
}
