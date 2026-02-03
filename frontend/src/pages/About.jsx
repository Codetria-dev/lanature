import { Link } from 'react-router-dom'
import Card from '../components/ui/Card'
import { ROUTES } from '../constants'
import { t } from '../i18n'

export default function About() {
  return (
    <div className="px-4 py-8 min-h-screen bg-gray-50">
      <div className="max-w-4xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">{t('about.title')}</h1>
          <p className="text-lg text-gray-600">{t('about.subtitle')}</p>
        </div>

        {/* Problem */}
        <Card className="mb-6">
          <Card.Header>
            <h2 className="text-xl font-semibold text-gray-900">{t('about.problem.title')}</h2>
          </Card.Header>
          <Card.Body>
            <p className="text-gray-700 mb-4">{t('about.problem.description')}</p>
            <ul className="space-y-2 list-disc list-inside text-gray-600">
              <li>{t('about.problem.point1')}</li>
              <li>{t('about.problem.point2')}</li>
              <li>{t('about.problem.point3')}</li>
              <li>{t('about.problem.point4')}</li>
            </ul>
          </Card.Body>
        </Card>

        {/* Who it's for */}
        <Card className="mb-6">
          <Card.Header>
            <h2 className="text-xl font-semibold text-gray-900">{t('about.audience.title')}</h2>
          </Card.Header>
          <Card.Body>
            <p className="text-gray-700 mb-4">{t('about.audience.description')}</p>
            <div className="grid md:grid-cols-2 gap-4">
              <div className="p-4 bg-green-50 rounded-lg border border-green-200">
                <h3 className="font-semibold text-gray-900 mb-2">{t('about.audience.ideal.title')}</h3>
                <p className="text-sm text-gray-600">{t('about.audience.ideal.description')}</p>
              </div>
              <div className="p-4 bg-blue-50 rounded-lg border border-blue-200">
                <h3 className="font-semibold text-gray-900 mb-2">{t('about.audience.multiPet.title')}</h3>
                <p className="text-sm text-gray-600">{t('about.audience.multiPet.description')}</p>
              </div>
            </div>
          </Card.Body>
        </Card>

        {/* What it doesn't do */}
        <Card className="mb-6 border-l-4 border-l-amber-500">
          <Card.Header className="bg-amber-50/50">
            <h2 className="text-xl font-semibold text-gray-900">{t('about.scope.title')}</h2>
          </Card.Header>
          <Card.Body>
            <p className="text-gray-700 mb-4">{t('about.scope.description')}</p>
            <ul className="space-y-2 list-disc list-inside text-gray-600">
              <li>{t('about.scope.not1')}</li>
              <li>{t('about.scope.not2')}</li>
              <li>{t('about.scope.not3')}</li>
              <li>{t('about.scope.not4')}</li>
            </ul>
          </Card.Body>
        </Card>

        {/* Roadmap */}
        <Card className="mb-6">
          <Card.Header>
            <h2 className="text-xl font-semibold text-gray-900">{t('about.roadmap.title')}</h2>
          </Card.Header>
          <Card.Body>
            <div className="space-y-4">
              <div className="flex items-start gap-4">
                <div className="flex-shrink-0 w-8 h-8 bg-green-500 rounded-full flex items-center justify-center text-white font-semibold text-sm">
                  ✓
                </div>
                <div>
                  <h3 className="font-semibold text-gray-900 mb-1">{t('about.roadmap.completed.title')}</h3>
                  <p className="text-sm text-gray-600">{t('about.roadmap.completed.description')}</p>
                </div>
              </div>
              
              <div className="flex items-start gap-4">
                <div className="flex-shrink-0 w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center text-white font-semibold text-sm">
                  1
                </div>
                <div>
                  <h3 className="font-semibold text-gray-900 mb-1">{t('about.roadmap.next.title')}</h3>
                  <p className="text-sm text-gray-600">{t('about.roadmap.next.description')}</p>
                </div>
              </div>
              
              <div className="flex items-start gap-4">
                <div className="flex-shrink-0 w-8 h-8 bg-gray-300 rounded-full flex items-center justify-center text-gray-600 font-semibold text-sm">
                  2
                </div>
                <div>
                  <h3 className="font-semibold text-gray-900 mb-1">{t('about.roadmap.future.title')}</h3>
                  <p className="text-sm text-gray-600">{t('about.roadmap.future.description')}</p>
                </div>
              </div>
            </div>
          </Card.Body>
        </Card>

        {/* CTA */}
        <div className="text-center">
          <Link to={ROUTES.REGISTER}>
            <button className="px-6 py-3 bg-green-600 hover:bg-green-700 text-white font-medium rounded-lg transition-colors">
              {t('about.cta')}
            </button>
          </Link>
        </div>
      </div>
    </div>
  )
}
