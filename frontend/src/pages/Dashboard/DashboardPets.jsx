import { Link } from 'react-router-dom'
import { ROUTES } from '../../constants'
import { t } from '../../i18n'

export default function DashboardPets({ pets }) {
  if (pets.length === 0) {
    return null
  }

  const visiblePets = pets.slice(0, 3)
  const remainingCount = pets.length - 3

  return (
    <section className="mb-12">
      <div className="flex flex-wrap items-center gap-2">
        {visiblePets.map(pet => (
          <span
            key={pet.id}
            className="inline-flex items-center px-3 py-1.5 rounded-full text-sm font-medium bg-gray-100 text-gray-700 border border-gray-200"
          >
            {pet.name}
          </span>
        ))}
        {remainingCount > 0 && (
          <Link
            to={ROUTES.PETS}
            className="inline-flex items-center px-3 py-1.5 rounded-full text-sm font-medium bg-gray-50 text-gray-600 border border-gray-200 hover:bg-gray-100 hover:text-gray-700 transition-colors"
          >
            +{remainingCount} {t('pets.more')}
          </Link>
        )}
      </div>
    </section>
  )
}
