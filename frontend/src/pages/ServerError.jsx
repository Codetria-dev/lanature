import { Link } from 'react-router-dom'
import { ROUTES } from '../constants'
import { t } from '../i18n'

export default function ServerError() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 px-4">
      <div className="text-center max-w-md">
        <div className="mb-8">
          <h1 className="text-9xl font-bold text-red-300 mb-4">500</h1>
          <h2 className="text-2xl font-semibold text-gray-900 mb-2">{t('error500.title')}</h2>
          <p className="text-gray-600 mb-4">{t('error500.description')}</p>
          <p className="text-sm text-gray-500">{t('error500.help')}</p>
        </div>
        
        <div className="space-y-4">
          <button 
            onClick={() => window.location.reload()}
            className="w-full px-6 py-3 bg-green-600 hover:bg-green-700 text-white font-medium rounded-lg transition-colors"
          >
            {t('error500.retry')}
          </button>
          <Link to={ROUTES.DASHBOARD}>
            <button className="w-full px-6 py-3 bg-gray-200 hover:bg-gray-300 text-gray-800 font-medium rounded-lg transition-colors">
              {t('error500.goHome')}
            </button>
          </Link>
        </div>
      </div>
    </div>
  )
}
