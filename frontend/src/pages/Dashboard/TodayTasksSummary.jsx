import { Link } from 'react-router-dom'
import { useMemo, useState, useEffect } from 'react'
import { ROUTES } from '../../constants'
import { t } from '../../i18n'
import { EmptyPetsState, EmptyRoutinesState, EmptyTodayTasksState } from './EmptyStates'
import { useTaskToggle } from './useTaskToggle'
import TaskItem from './TaskItem'

export default function TodayTasksSummary({ routines, pets, logs: initialLogs, onShowAlert }) {
  const [logs, setLogs] = useState(initialLogs)
  const { isRoutineCompleted, togglingRoutine, handleToggleRoutine } = useTaskToggle(logs, onShowAlert)

  useEffect(() => {
    setLogs(initialLogs)
  }, [initialLogs])

  const getTodayRoutines = () => {
    return routines
      .filter(r => r.active)
      .map(routine => {
        const routineTime = routine.time.split(':')
        const routineMinutes = parseInt(routineTime[0]) * 60 + parseInt(routineTime[1])
        return { ...routine, routineMinutes }
      })
      .sort((a, b) => a.routineMinutes - b.routineMinutes)
  }

  const allTodayRoutines = getTodayRoutines()
  const todayRoutines = allTodayRoutines.slice(0, 5)
  const hasMore = allTodayRoutines.length > 5
  const activeRoutines = routines.filter(r => r.active)

  const renderEmptyState = () => {
    if (pets.length === 0) return <EmptyPetsState />
    if (activeRoutines.length === 0) return <EmptyRoutinesState />
    return <EmptyTodayTasksState />
  }

  return (
    <section className="mb-10">
      <h2 className="text-lg font-medium mb-6 text-gray-900">
        {t('routines.nextCare')}
      </h2>
      
      {todayRoutines.length === 0 ? (
        renderEmptyState()
      ) : (
        <div>
          <div className="space-y-3">
            {todayRoutines.map(routine => {
              const pet = pets.find(p => p.id === routine.pet_id)
              const isCompleted = isRoutineCompleted(routine.id)
              const isToggling = togglingRoutine === routine.id
              
              return (
                <TaskItem
                  key={routine.id}
                  routine={routine}
                  pet={pet}
                  isCompleted={isCompleted}
                  isToggling={isToggling}
                  onToggle={() => handleToggleRoutine(routine, logs, setLogs)}
                />
              )
            })}
          </div>
          
          {hasMore && (
            <div className="mt-4">
              <Link to={ROUTES.ROUTINES} className="text-sm text-gray-600 hover:text-gray-900 underline underline-offset-2">
                {t('routines.viewAll')}
              </Link>
            </div>
          )}
        </div>
      )}
    </section>
  )
}
