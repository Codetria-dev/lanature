import { useMemo } from 'react'
import { t, formatDateShort, plural } from '../../i18n'

export default function DashboardSummary({ routines, pets, logs }) {
  const today = useMemo(() => {
    const date = new Date()
    return date.toISOString().split('T')[0]
  }, [])

  const todayTasksCount = useMemo(() => {
    return routines.filter(r => r.active).length
  }, [routines])

  const petsCount = useMemo(() => {
    return pets.length
  }, [pets])

  const lastActivity = useMemo(() => {
    if (!logs || logs.length === 0) return null
    
    const sortedLogs = [...logs].sort((a, b) => {
      return new Date(b.date) - new Date(a.date)
    })
    
    const lastLog = sortedLogs[0]
    if (!lastLog) return null
    
    const logDate = new Date(lastLog.date)
    const todayDate = new Date()
    const isToday = logDate.toDateString() === todayDate.toDateString()
    
    if (isToday) {
      return { text: t('dashboard.summary.lastActivityToday') }
    } else {
      return { text: t('dashboard.summary.lastActivityDate', { date: formatDateShort(lastLog.date) }) }
    }
  }, [logs])

  return (
    <div className="mb-8 pb-6 border-b border-gray-200">
      <div className="flex flex-wrap items-center gap-6 text-sm text-gray-600">
        <span>
          <span className="font-semibold text-gray-900">{todayTasksCount}</span>{' '}
          {plural('dashboard.summary.tasksToday', todayTasksCount)}
        </span>
        <span>
          <span className="font-semibold text-gray-900">{petsCount}</span>{' '}
          {plural('dashboard.summary.petsRegistered', petsCount)}
        </span>
        {lastActivity && (
          <span className="text-gray-500">
            {lastActivity.text}
          </span>
        )}
      </div>
    </div>
  )
}
