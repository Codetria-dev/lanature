import { useState, useMemo } from 'react'
import { useLogs } from '../../hooks/useLogs'
import { MESSAGES } from '../../constants'

export function useTaskToggle(logs, onShowAlert) {
  const { createLog, deleteLog, fetchLogs } = useLogs()
  const [togglingRoutine, setTogglingRoutine] = useState(null)

  const today = useMemo(() => {
    const date = new Date()
    return date.toISOString().split('T')[0]
  }, [])

  const isRoutineCompleted = (taskId) => {
    return logs.some(
      log => log.task_id === taskId && 
             log.date === today && 
             log.status === 'done'
    )
  }

  const getTodayLogId = (taskId) => {
    const log = logs.find(
      log => log.task_id === taskId && log.date === today
    )
    return log?.id
  }

  const handleToggleRoutine = async (routine, currentLogs, setLogs) => {
    setTogglingRoutine(routine.id)
    try {
      const isCompleted = isRoutineCompleted(routine.id)
      const logId = getTodayLogId(routine.id)

      if (isCompleted && logId) {
        const result = await deleteLog(logId)
        if (result.success) {
          await fetchLogs()
          setLogs(currentLogs.filter(l => l.id !== logId))
        }
      } else {
        const result = await createLog({
          task_id: routine.id,
          date: today,
          status: 'done'
        })
        if (result.success) {
          await fetchLogs()
          setLogs([...currentLogs, result.data])
        }
      }
    } catch (err) {
      if (onShowAlert) {
        onShowAlert({ type: 'error', message: MESSAGES.ERROR_GENERIC })
      }
    } finally {
      setTogglingRoutine(null)
    }
  }

  return {
    isRoutineCompleted,
    togglingRoutine,
    handleToggleRoutine
  }
}
