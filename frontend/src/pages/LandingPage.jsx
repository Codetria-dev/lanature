import { Link } from 'react-router-dom'
import Button from '../components/ui/Button'
import Card from '../components/ui/Card'
import LanguageSelector from '../components/ui/LanguageSelector'
import { ROUTES } from '../constants'
import { t } from '../i18n'

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-green-50 to-white">
      <nav className="bg-white shadow-sm">
        <div className="container-custom">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <span className="text-2xl font-bold text-brand-500">{t('appName')}</span>
            </div>
            <div className="flex items-center space-x-4">
              <LanguageSelector />
              <Link
                to={ROUTES.LOGIN}
                className="text-gray-700 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium"
              >
                {t('login')}
              </Link>
              <Link to={ROUTES.REGISTER}>
                <Button size="sm">{t('register')}</Button>
              </Link>
            </div>
          </div>
        </div>
      </nav>

      <div className="container-custom py-20">
        <div className="text-center">
          <h1 className="text-5xl font-extrabold text-gray-900 sm:text-6xl">
            {t('landing.title')}
            <span className="text-brand-500"> {t('landing.titleHighlight')}</span>
          </h1>
          <p className="mt-6 text-xl text-gray-500 max-w-3xl mx-auto">
            {t('landing.subtitle')}
          </p>
          <div className="mt-10">
            <Link to={ROUTES.REGISTER}>
              <Button size="lg">{t('landing.cta')}</Button>
            </Link>
          </div>
        </div>

        <div className="mt-20 grid grid-cols-1 md:grid-cols-3 gap-8">
          <Card shadow={false} className="text-center bg-gradient-to-br from-brand-50 to-emerald-50 shadow-lg hover:shadow-xl transition-all duration-300 border border-brand-100">
            <h3 className="text-xl font-semibold mb-2 text-brand-800">{t('landing.features.what.title')}</h3>
            <p className="text-gray-700">
              {t('landing.features.what.description')}
            </p>
          </Card>
          <Card shadow={false} className="text-center bg-gradient-to-br from-blue-50 to-cyan-50 shadow-lg hover:shadow-xl transition-all duration-300 border border-blue-100">
            <h3 className="text-xl font-semibold mb-2 text-blue-800">{t('landing.features.who.title')}</h3>
            <p className="text-gray-700">
              {t('landing.features.who.description')}
            </p>
          </Card>
          <Card shadow={false} className="text-center bg-gradient-to-br from-purple-50 to-pink-50 shadow-lg hover:shadow-xl transition-all duration-300 border border-purple-100">
            <h3 className="text-xl font-semibold mb-2 text-purple-800">{t('landing.features.benefits.title')}</h3>
            <p className="text-gray-700">
              {t('landing.features.benefits.description')}
            </p>
          </Card>
        </div>
      </div>
    </div>
  )
}
