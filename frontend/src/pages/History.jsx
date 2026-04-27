import { useState, useMemo } from 'react'
import { useLogs } from '../hooks/useLogs'
import { useRoutines } from '../hooks/useRoutines'
import { usePets } from '../hooks/usePets'
import PageHeader from '../components/layouts/PageHeader'
import EmptyState from '../components/layouts/EmptyState'
import Card from '../components/ui/Card'
import Button from '../components/ui/Button'
import Badge from '../components/ui/Badge'
import Select from '../components/ui/Select'
import Alert from '../components/ui/Alert'
import { MESSAGES, LOG_STATUS } from '../constants'
import { t, plural, formatDateShort } from '../i18n'
import ListSkeleton from '../components/ui/ListSkeleton'

export default function History() {
  const [filterPet, setFilterPet] = useState('all')
  const [filterStatus, setFilterStatus] = useState('all')
  const { logs, loading, error, updateLog, deleteLog } = useLogs({
    petId: filterPet,
    status: filterStatus,
  })
  const { routines } = useRoutines()
  const { pets } = usePets()
  const [alert, setAlert] = useState(null)

  const getRoutineInfo = (taskId) => {
    const routine = routines.find(r => r.id === taskId)
    if (!routine) return { type: t('history.taskNotFound'), pet_id: null }
    return routine
  }

  const getPetName = (petId) => {
    const pet = pets.find(p => p.id === petId)
    return pet ? pet.name : t('pets.notFound')
  }

  // Group logs by pet_id
  const logsByPet = useMemo(() => {
    const grouped = {}
    logs.forEach(log => {
      const routine = routines.find(r => r.id === log.task_id)
      const petId = routine?.pet_id
      
      if (petId) {
        if (!grouped[petId]) {
          grouped[petId] = []
        }
        grouped[petId].push(log)
      }
    })
    
    // Sort logs within each pet by date (newest first)
    Object.keys(grouped).forEach(petId => {
      grouped[petId].sort((a, b) => {
        return new Date(b.date) - new Date(a.date)
      })
    })
    
    return grouped
  }, [logs, routines])

  // Get pets that have logs
  const petsWithLogs = useMemo(() => {
    if (filterPet !== 'all') {
      // If filtering by specific pet, show only that pet
      const pet = pets.find(p => p.id === parseInt(filterPet))
      return pet ? [pet] : []
    }
    // Show all pets that have logs
    return pets.filter(pet => logsByPet[pet.id] && logsByPet[pet.id].length > 0)
  }, [pets, logsByPet, filterPet])

  const handleLogStatus = async (log, newStatus) => {
    const routine = getRoutineInfo(log.task_id)
    const result = await updateLog(log.id, {
      task_id: log.task_id,
      date: log.date,
      status: newStatus,
    })

    if (result.success) {
      setAlert({ type: 'success', message: t('history.statusUpdated') })
      setTimeout(() => setAlert(null), 5000)
    } else {
      setAlert({ type: 'error', message: result.error || MESSAGES.ERROR_GENERIC })
    }
  }

  const handleDelete = async (id) => {
    if (!window.confirm(MESSAGES.CONFIRM_DELETE)) return

    const result = await deleteLog(id)
    if (result.success) {
      setAlert({ type: 'success', message: t('history.recordDeleted') })
      setTimeout(() => setAlert(null), 5000)
    } else {
      setAlert({ type: 'error', message: result.error || MESSAGES.ERROR_GENERIC })
    }
  }

  const petOptions = [
    { value: 'all', label: t('history.allPets') },
    ...pets.map(pet => ({ value: pet.id, label: pet.name })),
  ]

  const statusOptions = [
    { value: 'all', label: t('history.all') },
    { value: LOG_STATUS.DONE, label: t('status.done') },
    { value: LOG_STATUS.SKIPPED, label: t('status.skipped') },
  ]

  if (loading) {
    return (
      <div className="px-4 py-6 min-h-screen">
        <div className="container-custom py-8">
          <div className="text-center py-4 text-gray-500 text-sm">
            {t('loadingStates.loadingHistory')}
          </div>
          <ListSkeleton count={4} showActions={true} />
        </div>
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

        <PageHeader title={t('history.title')} />

        {error && (
          <Alert variant="error" className="mb-6">
            {error}
          </Alert>
        )}

        <Card className="mb-4 p-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            <Select
              label={t('history.filterByPet')}
              value={filterPet}
              onChange={(e) => setFilterPet(e.target.value)}
              options={petOptions}
            />
            <Select
              label={t('history.filterByStatus')}
              value={filterStatus}
              onChange={(e) => setFilterStatus(e.target.value)}
              options={statusOptions}
            />
          </div>
        </Card>

        {logs.length === 0 ? (
        <EmptyState
          icon="history"
          title={t('history.noRecords')}
          description={t('history.noRecordsDescription')}
        />
      ) : petsWithLogs.length === 0 ? (
        <EmptyState
          icon="history"
          title={t('history.noRecords')}
          description={t('history.noRecordsDescription')}
        />
      ) : (
        <div className="space-y-4">
          {petsWithLogs.map(pet => {
            const petLogs = logsByPet[pet.id] || []
            if (petLogs.length === 0) return null

            return (
              <Card key={pet.id} className="border-l-4 border-l-brand-300">
                <Card.Header className="pb-3 border-b border-gray-200">
                  <div className="flex items-center gap-3">
                    <div>
                      <h2 className="text-xl font-bold text-gray-900">{pet.name}</h2>
                      <p className="text-sm text-gray-500">{pet.species}</p>
                    </div>
                    <Badge variant="default" className="ml-auto">
                      {petLogs.length} {plural('history.record', petLogs.length)}
                    </Badge>
                  </div>
                </Card.Header>
                <Card.Body className="pt-3">
                  <div className="space-y-2">
                    {petLogs.map(log => {
                      const routine = getRoutineInfo(log.task_id)
                      const isDone = log.status === LOG_STATUS.DONE

                      return (
                        <div
                          key={log.id}
                          className={`border-l-4 ${
                            isDone
                              ? 'border-l-green-500 bg-green-50/30'
                              : 'border-l-yellow-500 bg-yellow-50/30'
                          } p-3 rounded transition-all duration-200 hover:shadow-sm`}
                        >
                          <div className="flex items-center justify-between gap-3">
                            <div className="flex-1 flex items-center gap-3">
                              <Badge
                                variant={isDone ? 'success' : 'warning'}
                                className="text-xs"
                              >
                                {t(`status.${log.status}`)}
                              </Badge>
                              <div className="flex-1">
                                <h3 className="font-semibold text-gray-900">{routine.type}</h3>
                                <p className="text-xs text-gray-600 mt-1">
                                  {formatDateShort(log.date)}
                                </p>
                              </div>
                            </div>
                            <div className="flex gap-2">
                              {!isDone && (
                                <Button
                                  variant="primary"
                                  size="sm"
                                  onClick={() => handleLogStatus(log, LOG_STATUS.DONE)}
                                  className="text-xs px-3"
                                >
                                  {t('history.markAsDone')}
                                </Button>
                              )}
                              {log.status !== LOG_STATUS.SKIPPED && (
                                <Button
                                  variant="secondary"
                                  size="sm"
                                  onClick={() => handleLogStatus(log, LOG_STATUS.SKIPPED)}
                                  className="text-xs px-3"
                                >
                                  {t('history.markAsSkipped')}
                                </Button>
                              )}
                              <Button
                                variant="danger"
                                size="sm"
                                onClick={() => handleDelete(log.id)}
                                className="text-xs px-3"
                              >
                                {t('history.delete')}
                              </Button>
                            </div>
                          </div>
                        </div>
                      )
                    })}
                  </div>
                </Card.Body>
              </Card>
            )
          })}
        </div>
        )}
      </div>
    </div>
  )
}
