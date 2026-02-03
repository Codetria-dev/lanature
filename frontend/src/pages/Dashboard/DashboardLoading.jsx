import ListSkeleton from '../../components/ui/ListSkeleton'
import { t } from '../../i18n'

export default function DashboardLoading({ loadingPets }) {
  return (
    <div className="px-4 py-6">
      <div className="text-center py-4 text-gray-500 text-sm">
        {loadingPets ? t('loadingStates.loadingPets') : t('loadingStates.loadingRoutines')}
      </div>
      <ListSkeleton count={3} showActions={false} />
    </div>
  )
}
