import { useState } from 'react'
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
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)

  const isActive = (path) => location.pathname === path

  const navItems = [
    { path: ROUTES.DASHBOARD, label: t('dashboard.title') },
    { path: ROUTES.PETS, label: t('pets.title') },
    { path: ROUTES.ROUTINES, label: t('routines.title') },
    { path: ROUTES.HISTORY, label: t('history.title') },
  ]

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      <nav className="bg-white shadow-sm border-b border-gray-100">
        <div className="container-custom">
          <div className="flex justify-between h-16">
            <div className="flex items-center gap-2">
              {/* Mobile hamburger */}
              <button
                onClick={() => setMobileMenuOpen(true)}
                className="sm:hidden p-2 rounded-lg text-gray-600 hover:text-gray-900 hover:bg-gray-100 transition-all duration-200"
                aria-label="Open menu"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                </svg>
              </button>
              <div className="flex-shrink-0 flex items-center">
                <Link
                  to={ROUTES.DASHBOARD}
                  className="text-2xl font-bold text-brand-500 tracking-tight hover:text-brand-600 transition-colors duration-150"
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
                        ? 'border-brand-500 text-gray-900'
                        : 'border-transparent text-gray-600 hover:border-gray-300 hover:text-gray-900'
                    )}
                  >
                    {item.label}
                  </Link>
                ))}
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <span className="hidden sm:inline text-sm text-gray-700 font-medium">{user?.name}</span>
              <LanguageSelector />
              <Button variant="danger" size="sm" onClick={logout}>
                {t('logout')}
              </Button>
            </div>
          </div>
        </div>
      </nav>

      {/* Mobile drawer */}
      {mobileMenuOpen && (
        <div className="fixed inset-0 z-50 sm:hidden">
          <div
            className="fixed inset-0 bg-black/40 backdrop-blur-sm"
            onClick={() => setMobileMenuOpen(false)}
            style={{ animation: 'fadeIn 0.2s ease-out' }}
          />
          <div
            className="fixed inset-y-0 left-0 w-64 bg-white shadow-2xl flex flex-col"
            style={{ animation: 'slideInLeft 0.25s ease-out' }}
          >
            <div className="flex items-center justify-between p-4 border-b border-gray-100">
              <span className="text-xl font-bold text-brand-500">{t('appName')}</span>
              <button
                onClick={() => setMobileMenuOpen(false)}
                className="p-2 rounded-lg text-gray-400 hover:text-gray-600 hover:bg-gray-100 transition-all duration-150"
                aria-label="Close menu"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            <nav className="flex-1 p-4 space-y-1 overflow-y-auto">
              {navItems.map((item) => (
                <Link
                  key={item.path}
                  to={item.path}
                  onClick={() => setMobileMenuOpen(false)}
                  className={classNames(
                    'block px-4 py-3 rounded-lg text-sm font-medium transition-all duration-150',
                    isActive(item.path)
                      ? 'bg-brand-50 text-brand-700'
                      : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                  )}
                >
                  {item.label}
                </Link>
              ))}
            </nav>
            <div className="p-4 border-t border-gray-100">
              <p className="text-sm text-gray-500 truncate">{user?.name}</p>
            </div>
          </div>
        </div>
      )}
      <main className="container-custom py-8">
        {location.pathname !== ROUTES.DASHBOARD && (
          <div className="mb-6">
            <Link to={ROUTES.DASHBOARD}>
              <Button variant="ghost" size="sm">
                {t('navigation.home')}
              </Button>
            </Link>
          </div>
        )}
        {children}
      </main>
      <footer className="bg-white border-t border-gray-100 mt-auto">
        <div className="container-custom py-6">
          <div className="flex flex-col sm:flex-row justify-between items-center space-y-3 sm:space-y-0">
            <div className="text-sm text-gray-600">
              © {new Date().getFullYear()} LaNature. {t('footer.rights')}
            </div>
            <div className="flex space-x-6">
              <Link
                to={ROUTES.ABOUT}
                className="text-sm text-gray-600 hover:text-brand-600 transition-colors duration-150"
              >
                {t('navigation.about')}
              </Link>
              <Link
                to={ROUTES.CONTACT}
                className="text-sm text-gray-600 hover:text-brand-600 transition-colors duration-150"
              >
                {t('navigation.contact')}
              </Link>
            </div>
          </div>
        </div>
      </footer>
    </div>
  )
}
