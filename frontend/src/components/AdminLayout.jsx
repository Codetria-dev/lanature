import { Link } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import Button from './ui/Button'
import LanguageSelector from './ui/LanguageSelector'
import { ROUTES } from '../constants'
import { t } from '../i18n'

export default function AdminLayout({ children }) {
  const { user, logout } = useAuth()

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      <nav className="bg-white shadow-sm border-b border-gray-100">
        <div className="container-custom">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <span className="text-2xl font-bold text-green-600 tracking-tight">
                {t('appName')} - Admin
              </span>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-sm text-gray-700 font-medium">{user?.name}</span>
              <LanguageSelector />
              <Button variant="danger" size="sm" onClick={logout}>
                {t('logout')}
              </Button>
            </div>
          </div>
        </div>
      </nav>
      <main className="container-custom py-8">
        {children}
      </main>
      <footer className="bg-white border-t border-gray-100 mt-auto">
        <div className="container-custom py-6">
          <div className="flex flex-col sm:flex-row justify-between items-center space-y-3 sm:space-y-0">
            <div className="text-sm text-gray-500">
              © {new Date().getFullYear()} LaNature. Todos os direitos reservados.
            </div>
            <div className="flex space-x-6">
              <Link
                to={ROUTES.CONTACT}
                className="text-sm text-gray-500 hover:text-green-600 transition-colors duration-150"
              >
                Contato
              </Link>
            </div>
          </div>
        </div>
      </footer>
    </div>
  )
}
