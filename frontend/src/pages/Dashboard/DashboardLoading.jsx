import Skeleton from '../../components/ui/Skeleton'
import Card from '../../components/ui/Card'
import { t } from '../../i18n'

export default function DashboardLoading({ loadingPets }) {
  return (
    <div className="px-4 py-6 space-y-6">
      {/* Summary cards skeleton */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {[1, 2, 3].map((i) => (
          <Card key={i} className="p-5">
            <Skeleton variant="subtitle" width="50%" className="mb-3" />
            <Skeleton variant="title" width="30%" />
            <Skeleton variant="text" width="70%" className="mt-2" />
          </Card>
        ))}
      </div>

      {/* List skeleton */}
      <div className="text-center py-4 text-gray-500 text-sm">
        {loadingPets ? t('loadingStates.loadingPets') : t('loadingStates.loadingRoutines')}
      </div>
      <div className="space-y-4">
        {[1, 2, 3].map((i) => (
          <Card key={i} className="p-4">
            <div className="flex items-start gap-4">
              <Skeleton variant="avatar" rounded />
              <div className="flex-1 space-y-2">
                <Skeleton variant="title" width="60%" />
                <Skeleton variant="text" lines={2} />
              </div>
            </div>
          </Card>
        ))}
      </div>
    </div>
  )
}
