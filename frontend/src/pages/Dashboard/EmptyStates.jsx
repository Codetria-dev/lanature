import { t } from '../../i18n'

export function EmptyPetsState() {
  return (
    <div className="text-center py-8">
      <svg className="w-12 h-12 mx-auto text-gray-300 mb-3" fill="currentColor" viewBox="0 0 24 24">
        <path d="M11.5 1.5c.8 0 1.5.7 1.5 1.5 0 .8-.7 1.5-1.5 1.5S10 3.8 10 3c0-.8.7-1.5 1.5-1.5zm-5 2C7.3 3.5 8 4.2 8 5c0 .8-.7 1.5-1.5 1.5S5 5.8 5 5c0-.8.7-1.5 1.5-1.5zm10 0c.8 0 1.5.7 1.5 1.5 0 .8-.7 1.5-1.5 1.5S15 5.8 15 5c0-.8.7-1.5 1.5-1.5zM12 9c1.1 0 2 .9 2 2s-.9 2-2 2-2-.9-2-2 .9-2 2-2zM8 12c0 1.1-.9 2-2 2s-2-.9-2-2 .9-2 2-2 2 .9 2 2zm10 0c0 1.1-.9 2-2 2s-2-.9-2-2 .9-2 2-2 2 .9 2 2zM6.5 15.5c.8 0 1.5.7 1.5 1.5 0 .8-.7 1.5-1.5 1.5S5 17.8 5 17c0-.8.7-1.5 1.5-1.5zm11 0c.8 0 1.5.7 1.5 1.5 0 .8-.7 1.5-1.5 1.5S16 17.8 16 17c0-.8.7-1.5 1.5-1.5zM12 14c1.1 0 2 .9 2 2s-.9 2-2 2-2-.9-2-2 .9-2 2-2z"/>
      </svg>
      <p className="text-gray-600 text-sm">{t('pets.onboarding.description')}</p>
    </div>
  )
}

export function EmptyRoutinesState() {
  return (
    <div className="text-center py-8">
      <svg className="w-12 h-12 mx-auto text-gray-300 mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth={1.5}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M9 12h3.75M9 15h3.75M9 18h3.75m3 .75H18a2.25 2.25 0 002.25-2.25V6.108c0-1.135-.845-2.098-1.976-2.192a48.424 48.424 0 00-1.123-.08m-5.801 0c-.065.21-.1.433-.1.664 0 .414.336.75.75.75h4.5a.75.75 0 00.75-.75 2.25 2.25 0 00-.1-.664m-5.8 0A2.251 2.251 0 0113.5 2.25H15a2.25 2.25 0 012.15 1.586m-5.8 0c-.376.023-.75.05-1.124.08C9.095 4.01 8.25 4.973 8.25 6.108V8.25m0 0H4.875c-.621 0-1.125.504-1.125 1.125v11.25c0 .621.504 1.125 1.125 1.125h9.75c.621 0 1.125-.504 1.125-1.125V9.375c0-.621-.504-1.125-1.125-1.125H8.25zM6.75 12h.008v.008H6.75V12zm0 3h.008v.008H6.75V15zm0 3h.008v.008H6.75V18z"/>
      </svg>
      <p className="text-gray-600 text-sm">{t('routines.onboarding.description')}</p>
    </div>
  )
}

export function EmptyTodayTasksState() {
  return (
    <div className="text-center py-8">
      <svg className="w-12 h-12 mx-auto text-gray-300 mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth={1.5}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
      </svg>
      <p className="text-gray-600 text-sm">{t('routines.noneToday')}</p>
    </div>
  )
}
