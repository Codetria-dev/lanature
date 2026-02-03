import { useState, useMemo, useEffect } from 'react'
import { useRoutines } from '../hooks/useRoutines'
import { usePets } from '../hooks/usePets'
import { useLogs } from '../hooks/useLogs'
import PageHeader from '../components/layouts/PageHeader'
import EmptyState from '../components/layouts/EmptyState'
import Card from '../components/ui/Card'
import Button from '../components/ui/Button'
import Badge from '../components/ui/Badge'
import Modal from '../components/ui/Modal'
import RoutineForm from '../components/forms/RoutineForm'
import Alert from '../components/ui/Alert'
import { MESSAGES, LOG_STATUS } from '../constants'
import { t } from '../i18n'
import ListSkeleton from '../components/ui/ListSkeleton'

export default function Routines() {
  const { routines, loading, error, createRoutine, updateRoutine, deleteRoutine, toggleActive, fetchRoutines } = useRoutines()
  const { pets } = usePets()
  const { logs, createLog, deleteLog, fetchLogs } = useLogs()
  const [showModal, setShowModal] = useState(false)
  const [editingRoutine, setEditingRoutine] = useState(null)
  const [selectedPetId, setSelectedPetId] = useState(null)
  const [submitLoading, setSubmitLoading] = useState(false)
  const [alert, setAlert] = useState(null)
  const [togglingTask, setTogglingTask] = useState(null)

  // Get today's date in YYYY-MM-DD format
  const today = useMemo(() => {
    const date = new Date()
    return date.toISOString().split('T')[0]
  }, [])

  // Fetch logs on mount
  useEffect(() => {
    fetchLogs()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  // Helper function to convert time (HH:MM) to minutes for sorting
  const timeToMinutes = (timeString) => {
    if (!timeString) return 0
    const [hours, minutes] = timeString.split(':').map(Number)
    return (hours || 0) * 60 + (minutes || 0)
  }

  // Group tasks by pet_id and sort by time (24-hour format)
  const routinesByPet = useMemo(() => {
    const grouped = {}
    routines.forEach(task => {
      if (!grouped[task.pet_id]) {
        grouped[task.pet_id] = []
      }
      grouped[task.pet_id].push(task)
    })
    
    // Sort tasks within each pet group by time (ascending - earliest first)
    Object.keys(grouped).forEach(petId => {
      grouped[petId].sort((a, b) => {
        const timeA = timeToMinutes(a.time)
        const timeB = timeToMinutes(b.time)
        return timeA - timeB
      })
    })
    
    return grouped
  }, [routines])

  const handleSubmit = async (formData) => {
    setSubmitLoading(true)
    try {
      let result
      if (editingRoutine) {
        result = await updateRoutine(editingRoutine.id, formData)
      } else {
        result = await createRoutine(formData)
      }

      if (result.success) {
        setShowModal(false)
        setEditingRoutine(null)
        setSelectedPetId(null)
        await fetchRoutines()
        setAlert({ type: 'success', message: editingRoutine ? t('routines.taskUpdated') : t('routines.taskAdded') })
        setTimeout(() => setAlert(null), 5000)
      } else {
        setAlert({ type: 'error', message: result.error || MESSAGES.ERROR_GENERIC })
      }
    } catch (err) {
      setAlert({ type: 'error', message: MESSAGES.ERROR_GENERIC })
    } finally {
      setSubmitLoading(false)
    }
  }

  const handleEdit = (routine) => {
    setEditingRoutine(routine)
    setShowModal(true)
  }

  const handleDelete = async (id) => {
    if (!window.confirm(MESSAGES.CONFIRM_DELETE)) return

    const result = await deleteRoutine(id)
    if (result.success) {
      await fetchRoutines()
      setAlert({ type: 'success', message: t('routines.taskDeleted') })
      setTimeout(() => setAlert(null), 5000)
    } else {
      setAlert({ type: 'error', message: result.error || MESSAGES.ERROR_GENERIC })
    }
  }

  const handleToggleActive = async (routine) => {
    const result = await toggleActive(routine)
    if (result.success) {
      await fetchRoutines()
      setAlert({ type: 'success', message: routine.active ? t('routines.taskDeactivated') : t('routines.taskActivated') })
      setTimeout(() => setAlert(null), 5000)
    }
  }

  const openModal = (petId = null) => {
    if (pets.length === 0) {
      setAlert({ type: 'warning', message: t('routines.noPetsDescription') })
      return
    }
    setEditingRoutine(null)
    setSelectedPetId(petId)
    setShowModal(true)
  }

  const closeModal = () => {
    setShowModal(false)
    setEditingRoutine(null)
    setSelectedPetId(null)
  }

  const getPetName = (petId) => {
    const pet = pets.find(p => p.id === petId)
    return pet ? pet.name : t('pets.notFound')
  }

  // Check if a task is completed today
  const isTaskCompletedToday = (taskId) => {
    return logs.some(
      log => log.task_id === taskId && 
             log.date === today && 
             log.status === LOG_STATUS.DONE
    )
  }

  // Get log ID for a task today
  const getTodayLogId = (taskId) => {
    const log = logs.find(
      log => log.task_id === taskId && log.date === today
    )
    return log?.id
  }

  // Handle task completion toggle
  const handleTaskToggle = async (task) => {
    if (!task.active) {
      setAlert({ type: 'warning', message: t('routines.inactiveCannotComplete') })
      return
    }

    setTogglingTask(task.id)
    try {
      const isCompleted = isTaskCompletedToday(task.id)
      const logId = getTodayLogId(task.id)

      if (isCompleted && logId) {
        // Unmark: delete the log
        const result = await deleteLog(logId)
        if (result.success) {
          await fetchLogs()
          setAlert({ type: 'success', message: t('routines.taskUnmarked') })
          setTimeout(() => setAlert(null), 4000)
        }
      } else {
        // Mark as done: create log
        const result = await createLog({
          task_id: task.id,
          date: today,
          status: LOG_STATUS.DONE
        })
        if (result.success) {
          await fetchLogs()
          setAlert({ type: 'success', message: t('routines.taskMarkedCompleted') })
          setTimeout(() => setAlert(null), 4000)
        }
      }
    } catch (err) {
      setAlert({ type: 'error', message: MESSAGES.ERROR_GENERIC })
    } finally {
      setTogglingTask(null)
    }
  }

  if (loading) {
    return (
      <div className="px-4 py-6">
        <div className="text-center py-4 text-gray-500 text-sm">
          {t('loadingStates.loadingRoutines')}
        </div>
        <ListSkeleton count={4} showActions={true} />
      </div>
    )
  }

  return (
    <div className="px-4 py-6 min-h-screen">
      <div className="container-custom">
        {alert && (
          <div className="mb-4 fixed top-20 left-1/2 transform -translate-x-1/2 z-50 w-full max-w-2xl px-4">
            <Alert variant={alert.type} onClose={() => setAlert(null)}>
              {alert.message}
            </Alert>
          </div>
        )}

        <PageHeader
          title={t('routines.title')}
          action={() => openModal()}
          actionLabel={t('routines.addTask')}
          actionClassName="!bg-[#7fa653] hover:!bg-[#6a8a45] text-white shadow-md hover:shadow-lg font-semibold"
          isProminent={routines.length === 0 && pets.length > 0}
        />

        {error && (
          <Alert variant="error" className="mb-6">
            {error}
          </Alert>
        )}

        {pets.length === 0 ? (
        <EmptyState
          title={t('routines.noPetsYet')}
          description={t('routines.noPetsDescription')}
        />
      ) : (
        <div className="space-y-6">
          {pets.map(pet => {
            const petTasks = routinesByPet[pet.id] || []
            return (
              <Card key={pet.id}>
                <Card.Header className="pb-4">
                  <div>
                    <h2 className="text-xl font-bold text-gray-900">{pet.name}</h2>
                    <p className="text-sm text-gray-500 mt-1">{pet.species}</p>
                  </div>
                </Card.Header>
                <Card.Body>
                  {petTasks.length === 0 ? (
                    <div className="text-center py-6 text-gray-500">
                      <p className="mb-3">{t('routines.noTasksForPet')} {pet.name}</p>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => openModal(pet.id)}
                        className="!bg-gray-100 hover:!bg-gray-200 text-gray-700"
                      >
                        {t('routines.addFirstTask')}
                      </Button>
                    </div>
                  ) : (
                    <div className="space-y-3">
                      {petTasks.map(task => {
                        const isCompleted = isTaskCompletedToday(task.id)
                        const isToggling = togglingTask === task.id
                        
                        return (
                          <div
                            key={task.id}
                            className={`flex items-center justify-between p-4 rounded-lg ${
                              isCompleted 
                                ? 'bg-gray-50' 
                                : 'bg-white border border-gray-200'
                            } ${
                              !task.active ? 'opacity-50' : ''
                            } transition-all duration-200 hover:shadow-sm`}
                          >
                            <div className="flex-1 flex items-center gap-4">
                              <input
                                type="checkbox"
                                checked={isCompleted}
                                onChange={() => handleTaskToggle(task)}
                                disabled={isToggling || !task.active}
                                className="w-5 h-5 text-green-600 border-gray-300 rounded focus:ring-2 focus:ring-green-500 focus:ring-offset-0 cursor-pointer disabled:opacity-50 transition-all duration-150"
                              />
                              <div className="px-2 py-1 rounded text-xs font-medium bg-gray-100 text-gray-700">
                                {task.time}
                              </div>
                              <div className="flex-1">
                                <h3 className={`font-medium ${isCompleted ? 'line-through text-gray-500' : 'text-gray-900'}`}>
                                  {task.type}
                                </h3>
                                <p className="text-xs text-gray-500 mt-0.5">{task.frequency}</p>
                              </div>
                              {!task.active && (
                                <Badge variant="default" className="text-xs">
                                  {t('routines.inactiveStatus')}
                                </Badge>
                              )}
                              {isCompleted && task.active && (
                                <Badge variant="default" className="text-xs bg-green-50 text-green-700">
                                  {t('routines.completedToday')}
                                </Badge>
                              )}
                            </div>
                            <div className="flex gap-2 ml-3">
                              <Button
                                variant="secondary"
                                size="sm"
                                onClick={() => handleEdit(task)}
                                className="text-xs px-3"
                              >
                                {t('routines.edit')}
                              </Button>
                              <Button
                                variant="danger"
                                size="sm"
                                onClick={() => handleDelete(task.id)}
                                className="text-xs px-3"
                              >
                                {t('routines.delete')}
                              </Button>
                            </div>
                          </div>
                        )
                      })}
                    </div>
                  )}
                </Card.Body>
              </Card>
            )
          })}
        </div>
        )}

        <Modal
          isOpen={showModal}
          onClose={closeModal}
          title={editingRoutine ? t('routines.editTask') : t('routines.addTaskToRoutine')}
          size="md"
        >
          <RoutineForm
            routine={editingRoutine}
            pets={pets}
            onSubmit={handleSubmit}
            onCancel={closeModal}
            loading={submitLoading}
            defaultPetId={selectedPetId}
          />
        </Modal>
      </div>
    </div>
  )
}
