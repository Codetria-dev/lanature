import { useState, useEffect, useMemo } from 'react'
import { usePets } from '../hooks/usePets'
import { useRoutines } from '../hooks/useRoutines'
import { useLogs } from '../hooks/useLogs'
import { Link } from 'react-router-dom'
import Card from '../components/ui/Card'
import Button from '../components/ui/Button'
import Modal from '../components/ui/Modal'
import PetForm from '../components/forms/PetForm'
import Alert from '../components/ui/Alert'
import { ROUTES, MESSAGES } from '../constants'
import { t } from '../i18n'
import initialBg from '@assets/initial.png'

export default function Dashboard() {
  const { pets, loading: petsLoading, createPet } = usePets()
  const { routines, loading: routinesLoading } = useRoutines()
  const { logs, createLog, deleteLog, fetchLogs } = useLogs()
  const [showPetModal, setShowPetModal] = useState(false)
  const [submitLoading, setSubmitLoading] = useState(false)
  const [alert, setAlert] = useState(null)
  const [togglingRoutine, setTogglingRoutine] = useState(null)

  // Get today's date in YYYY-MM-DD format
  const today = useMemo(() => {
    const date = new Date()
    return date.toISOString().split('T')[0]
  }, [])

  // Fetch logs on mount and when routines are loaded
  useEffect(() => {
    if (!routinesLoading && routines.length > 0) {
      fetchLogs()
    }
  }, [routinesLoading, routines.length])

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

  // Check if a routine task is completed today
  const isRoutineCompleted = (taskId) => {
    return logs.some(
      log => log.task_id === taskId && 
             log.date === today && 
             log.status === 'done'
    )
  }

  // Get log ID for a routine task today
  const getTodayLogId = (taskId) => {
    const log = logs.find(
      log => log.task_id === taskId && log.date === today
    )
    return log?.id
  }

  const handleToggleRoutine = async (routine) => {
    setTogglingRoutine(routine.id)
    try {
      const isCompleted = isRoutineCompleted(routine.id)
      const logId = getTodayLogId(routine.id)

      if (isCompleted && logId) {
        // Unmark: delete the log
        const result = await deleteLog(logId)
        if (result.success) {
          await fetchLogs()
        }
      } else {
        // Mark as done: create log
        const result = await createLog({
          task_id: routine.id,
          date: today,
          status: 'done'
        })
        if (result.success) {
          await fetchLogs()
        }
      }
    } catch (err) {
      setAlert({ type: 'error', message: MESSAGES.ERROR_GENERIC })
    } finally {
      setTogglingRoutine(null)
    }
  }

  const loading = petsLoading || routinesLoading

  if (loading) {
    return (
      <div className="px-4 py-6">
        <div className="text-center py-12">{t('loading')}</div>
      </div>
    )
  }

  const todayRoutines = getTodayRoutines()
  const activeRoutines = routines.filter(r => r.active)

  const handlePetSubmit = async (formData) => {
    setSubmitLoading(true)
    try {
      const result = await createPet(formData)
      if (result.success) {
        setShowPetModal(false)
        setAlert({ type: 'success', message: MESSAGES.SUCCESS_CREATE })
        setTimeout(() => setAlert(null), 3000)
      } else {
        setAlert({ type: 'error', message: result.error || MESSAGES.ERROR_GENERIC })
      }
    } catch (err) {
      setAlert({ type: 'error', message: MESSAGES.ERROR_GENERIC })
    } finally {
      setSubmitLoading(false)
    }
  }

  return (
    <div 
      className="px-4 py-6 min-h-screen relative"
      style={{
        backgroundImage: `url(${initialBg})`,
        backgroundSize: 'cover',
        backgroundPosition: 'center',
        backgroundRepeat: 'no-repeat',
      }}
    >
      {/* Overlay for better readability */}
      <div className="absolute inset-0 bg-white/80 backdrop-blur-sm"></div>
      
      <div className="relative z-10">
        {alert && (
          <div className="mb-4">
            <Alert variant={alert.type} onClose={() => setAlert(null)}>
              {alert.message}
            </Alert>
          </div>
        )}
        
        <h1 className="text-3xl font-bold text-gray-900 mb-6">{t('dashboard')}</h1>

      {/* Next Care - Full width */}
      <Card className="mb-6">
        <Card.Header>
          <h2 className="text-xl font-semibold">{t('routines.nextCare')}</h2>
        </Card.Header>
        <Card.Body>
          {todayRoutines.length === 0 ? (
            <p className="text-gray-500 mb-4">
              {activeRoutines.length === 0
                ? t('routines.noneActive')
                : t('routines.noneToday')}
            </p>
          ) : (
            <div className="space-y-2">
              {todayRoutines.map(routine => {
                const pet = pets.find(p => p.id === routine.pet_id)
                const isCompleted = isRoutineCompleted(routine.id)
                const isToggling = togglingRoutine === routine.id
                
                return (
                  <div
                    key={routine.id}
                    className={`flex items-center justify-between p-4 rounded-lg transition-all duration-200 ${
                      isCompleted 
                        ? 'bg-green-50/80 border border-green-200/60 shadow-sm' 
                        : 'bg-white border border-gray-200 hover:border-green-300 hover:shadow-sm'
                    }`}
                  >
                    <div className="flex items-center space-x-3 flex-1">
                      <input
                        type="checkbox"
                        checked={isCompleted}
                        onChange={() => handleToggleRoutine(routine)}
                        disabled={isToggling}
                        className="w-5 h-5 text-green-600 border-gray-300 rounded focus:ring-2 focus:ring-green-500 focus:ring-offset-0 cursor-pointer disabled:opacity-50 transition-all duration-150"
                      />
                      <div className="flex-1">
                        <p className={`text-sm font-medium tracking-tight ${isCompleted ? 'line-through text-gray-500' : 'text-gray-900'}`}>
                          {routine.type}
                        </p>
                        <p className="text-xs text-gray-500 mt-0.5">
                          {pet?.name} - {routine.time}
                        </p>
                      </div>
                    </div>
                  </div>
                )
              })}
            </div>
          )}
        </Card.Body>
        <Card.Footer>
          <Link to={ROUTES.ROUTINES}>
            <Button variant="ghost" size="sm">
              {t('routines.viewAll')}
            </Button>
          </Link>
        </Card.Footer>
      </Card>

      {/* Registered Pets - Smaller grid below */}
      <Card className="mb-8">
        <Card.Header>
          <h2 className="text-xl font-semibold">{t('pets.registered')}</h2>
        </Card.Header>
        <Card.Body>
          {pets.length === 0 ? (
            <p className="text-gray-500 mb-4">{t('pets.none')}</p>
          ) : (
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
              {pets.map(pet => (
                <div
                  key={pet.id}
                  className="flex flex-col items-center p-4 bg-white border border-gray-200 rounded-lg text-center hover:border-green-300 hover:shadow-sm transition-all duration-200 cursor-pointer"
                >
                  <div className="text-3xl mb-2">🐾</div>
                  <p className="font-medium text-sm text-gray-900 tracking-tight">{pet.name}</p>
                  <p className="text-xs text-gray-500 mt-0.5">{pet.species}</p>
                </div>
              ))}
            </div>
          )}
        </Card.Body>
        <Card.Footer>
          <Link to={ROUTES.PETS}>
            <Button variant="ghost" size="sm">
              {t('pets.manage')}
            </Button>
          </Link>
        </Card.Footer>
      </Card>

      <Card>
        <Card.Header>
          <h2 className="text-xl font-semibold">{t('actions.quickActions')}</h2>
        </Card.Header>
        <Card.Body>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div 
              onClick={() => setShowPetModal(true)}
              className="p-5 border-2 border-green-200 rounded-lg hover:border-green-400 hover:bg-green-50/50 transition-all duration-200 cursor-pointer hover:shadow-sm active:scale-[0.98]"
            >
              <p className="font-medium text-sm text-gray-900 tracking-tight">{t('actions.addPet')}</p>
            </div>
            <Link to={ROUTES.ROUTINES}>
              <div className="p-5 border-2 border-green-200 rounded-lg hover:border-green-400 hover:bg-green-50/50 transition-all duration-200 cursor-pointer hover:shadow-sm active:scale-[0.98]">
                <p className="font-medium text-sm text-gray-900 tracking-tight">{t('actions.createRoutine')}</p>
              </div>
            </Link>
            <Link to={ROUTES.HISTORY}>
              <div className="p-5 border-2 border-green-200 rounded-lg hover:border-green-400 hover:bg-green-50/50 transition-all duration-200 cursor-pointer hover:shadow-sm active:scale-[0.98]">
                <p className="font-medium text-sm text-gray-900 tracking-tight">{t('actions.viewHistory')}</p>
              </div>
            </Link>
          </div>
        </Card.Body>
      </Card>

      <Modal
        isOpen={showPetModal}
        onClose={() => setShowPetModal(false)}
        title={t('pets.add')}
        size="md"
      >
        <PetForm
          onSubmit={handlePetSubmit}
          onCancel={() => setShowPetModal(false)}
          loading={submitLoading}
        />
      </Modal>
      </div>
    </div>
  )
}
