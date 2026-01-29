import { Link, useLocation } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import Button from './ui/Button'
import LanguageSelector from './ui/LanguageSelector'
import { ROUTES } from '../constants'
import classNames from '../utils/classNames'
import { t } from '../i18n'

export default function Layout({ children }) {
  const { user, logout } = useAuth()
  const location = useLocation()

  const isActive = (path) => location.pathname === path

  const navItems = [
    { path: ROUTES.DASHBOARD, label: t('dashboard') },
    { path: ROUTES.PETS, label: t('pets') },
    { path: ROUTES.ROUTINES, label: t('routines') },
    { path: ROUTES.HISTORY, label: t('history') },
  ]

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      <nav className="bg-white shadow-sm border-b border-gray-100">
        <div className="container-custom">
          <div className="flex justify-between h-16">
            <div className="flex">
              <div className="flex-shrink-0 flex items-center">
                <Link 
                  to={ROUTES.DASHBOARD} 
                  className="text-2xl font-bold text-green-600 tracking-tight hover:text-green-700 transition-colors duration-150"
                >
                  {t('appName')}
                </Link>
              </div>
              <div className="hidden sm:ml-8 sm:flex sm:space-x-1">
                {navItems.map((item) => (
                  <Link
                    key={item.path}
                    to={item.path}
                    className={classNames(
                      'inline-flex items-center px-3 py-2 border-b-2 text-sm font-medium transition-all duration-200',
                      isActive(item.path)
                        ? 'border-green-500 text-gray-900'
                        : 'border-transparent text-gray-600 hover:border-gray-300 hover:text-gray-900'
                    )}
                  >
                    {item.label}
                  </Link>
                ))}
              </div>
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
