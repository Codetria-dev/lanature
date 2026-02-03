import { t } from '../../i18n'

export function EmptyPetsState() {
  return (
    <p className="text-gray-500 text-sm">
      {t('pets.onboarding.description')}
    </p>
  )
}

export function EmptyRoutinesState() {
  return (
    <p className="text-gray-500 text-sm">
      {t('routines.onboarding.description')}
    </p>
  )
}

export function EmptyTodayTasksState() {
  return (
    <p className="text-gray-500 text-sm">
      {t('routines.noneToday')}
    </p>
  )
}
