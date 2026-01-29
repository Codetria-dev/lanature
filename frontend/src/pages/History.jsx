import { useState } from 'react'
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
import { MESSAGES, LOG_STATUS, LOG_STATUS_LABELS } from '../constants'
import backgroundBg from '@assets/background.png'

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
    if (!routine) return { type: 'Tarefa não encontrada', pet_id: null }
    return routine
  }

  const getPetName = (petId) => {
    const pet = pets.find(p => p.id === petId)
    return pet ? pet.name : 'Pet não encontrado'
  }

  const handleLogStatus = async (log, newStatus) => {
    const routine = getRoutineInfo(log.task_id)
    const result = await updateLog(log.id, {
      task_id: log.task_id,
      date: log.date,
      status: newStatus,
    })

    if (result.success) {
      setAlert({ type: 'success', message: 'Status atualizado com sucesso!' })
      setTimeout(() => setAlert(null), 3000)
    } else {
      setAlert({ type: 'error', message: result.error || MESSAGES.ERROR_GENERIC })
    }
  }

  const handleDelete = async (id) => {
    if (!window.confirm(MESSAGES.CONFIRM_DELETE)) return

    const result = await deleteLog(id)
    if (result.success) {
      setAlert({ type: 'success', message: 'Registro excluído com sucesso!' })
      setTimeout(() => setAlert(null), 3000)
    } else {
      setAlert({ type: 'error', message: result.error || MESSAGES.ERROR_GENERIC })
    }
  }

  const petOptions = [
    { value: 'all', label: 'Todos os pets' },
    ...pets.map(pet => ({ value: pet.id, label: pet.name })),
  ]

  const statusOptions = [
    { value: 'all', label: 'Todos' },
    { value: LOG_STATUS.DONE, label: LOG_STATUS_LABELS[LOG_STATUS.DONE] },
    { value: LOG_STATUS.SKIPPED, label: LOG_STATUS_LABELS[LOG_STATUS.SKIPPED] },
  ]

  if (loading) {
    return (
      <div 
        className="px-4 py-6 min-h-screen relative"
        style={{
          backgroundImage: `url(${backgroundBg})`,
          backgroundSize: 'cover',
          backgroundPosition: 'center',
          backgroundRepeat: 'no-repeat',
        }}
      >
        <div className="absolute inset-0 bg-white/80 backdrop-blur-sm"></div>
        <div className="relative z-10 text-center py-12">{MESSAGES.LOADING}</div>
      </div>
    )
  }

  return (
    <div 
      className="px-4 py-6 min-h-screen relative"
      style={{
        backgroundImage: `url(${backgroundBg})`,
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

        <PageHeader title="Histórico" />

        {error && (
          <Alert variant="error" className="mb-6">
            {error}
          </Alert>
        )}

        <Card className="mb-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <Select
            label="Filtrar por Pet"
            value={filterPet}
            onChange={(e) => setFilterPet(e.target.value)}
            options={petOptions}
          />
          <Select
            label="Filtrar por Status"
            value={filterStatus}
            onChange={(e) => setFilterStatus(e.target.value)}
            options={statusOptions}
          />
        </div>
        </Card>

        {logs.length === 0 ? (
        <EmptyState
          title="Nenhum registro no histórico ainda"
          description="Os registros de execução das rotinas aparecerão aqui"
          icon="📋"
        />
      ) : (
        <div className="space-y-4">
          {logs.map(log => {
            const routine = getRoutineInfo(log.task_id)
            const petName = routine.pet_id ? getPetName(routine.pet_id) : 'N/A'

            return (
              <Card
                key={log.id}
                className={`card-hover ${
                  log.status === LOG_STATUS.DONE
                    ? 'border-l-4 border-green-500'
                    : 'border-l-4 border-green-400'
                }`}
              >
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <div className="flex items-center space-x-3 mb-2">
                      <h3 className="text-xl font-semibold">{routine.type}</h3>
                      <Badge
                        variant={log.status === LOG_STATUS.DONE ? 'success' : 'warning'}
                      >
                        {LOG_STATUS_LABELS[log.status]}
                      </Badge>
                    </div>
                    <div className="space-y-1 text-gray-600">
                      <p>
                        <span className="font-medium">Pet:</span> {petName}
                      </p>
                      <p>
                        <span className="font-medium">Data:</span>{' '}
                        {new Date(log.date).toLocaleDateString('pt-BR')}
                      </p>
                    </div>
                  </div>
                  <div className="flex flex-col space-y-2 ml-4">
                    {log.status !== LOG_STATUS.DONE && (
                      <Button
                        variant="success"
                        size="sm"
                        onClick={() => handleLogStatus(log, LOG_STATUS.DONE)}
                        className="!bg-[#7fa653] hover:!bg-[#6a8a45] text-white"
                      >
                        Marcar como Feito
                      </Button>
                    )}
                    {log.status !== LOG_STATUS.SKIPPED && (
                      <Button
                        variant="warning"
                        size="sm"
                        onClick={() => handleLogStatus(log, LOG_STATUS.SKIPPED)}
                        className="!bg-[#76bd9b] hover:!bg-[#65a888] text-white"
                      >
                        Marcar como Pulado
                      </Button>
                    )}
                    <Button
                      variant="danger"
                      size="sm"
                      onClick={() => handleDelete(log.id)}
                      className="!bg-[#cfe0bc] hover:!bg-[#b8d09f] text-gray-800"
                    >
                      Excluir
                    </Button>
                  </div>
                </div>
              </Card>
            )
          })}
        </div>
        )}
      </div>
    </div>
  )
}
