import { useState, useMemo } from 'react'
import { useRoutines } from '../hooks/useRoutines'
import { usePets } from '../hooks/usePets'
import PageHeader from '../components/layouts/PageHeader'
import EmptyState from '../components/layouts/EmptyState'
import Card from '../components/ui/Card'
import Button from '../components/ui/Button'
import Badge from '../components/ui/Badge'
import Modal from '../components/ui/Modal'
import RoutineForm from '../components/forms/RoutineForm'
import Alert from '../components/ui/Alert'
import { MESSAGES, LOG_STATUS, LOG_STATUS_LABELS } from '../constants'
import routineBg from '@assets/routine.png'

export default function Routines() {
  const { routines, loading, error, createRoutine, updateRoutine, deleteRoutine, toggleActive, fetchRoutines } = useRoutines()
  const { pets } = usePets()
  const [showModal, setShowModal] = useState(false)
  const [editingRoutine, setEditingRoutine] = useState(null)
  const [selectedPetId, setSelectedPetId] = useState(null)
  const [submitLoading, setSubmitLoading] = useState(false)
  const [alert, setAlert] = useState(null)

  // Group tasks by pet_id
  const routinesByPet = useMemo(() => {
    const grouped = {}
    routines.forEach(task => {
      if (!grouped[task.pet_id]) {
        grouped[task.pet_id] = []
      }
      grouped[task.pet_id].push(task)
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
        setAlert({ type: 'success', message: editingRoutine ? 'Tarefa atualizada com sucesso!' : 'Tarefa adicionada com sucesso!' })
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

  const handleEdit = (routine) => {
    setEditingRoutine(routine)
    setShowModal(true)
  }

  const handleDelete = async (id) => {
    if (!window.confirm(MESSAGES.CONFIRM_DELETE)) return

    const result = await deleteRoutine(id)
    if (result.success) {
      await fetchRoutines()
      setAlert({ type: 'success', message: 'Tarefa excluída com sucesso!' })
      setTimeout(() => setAlert(null), 3000)
    } else {
      setAlert({ type: 'error', message: result.error || MESSAGES.ERROR_GENERIC })
    }
  }

  const handleToggleActive = async (routine) => {
    const result = await toggleActive(routine)
    if (result.success) {
      await fetchRoutines()
      setAlert({ type: 'success', message: routine.active ? 'Tarefa desativada!' : 'Tarefa ativada!' })
      setTimeout(() => setAlert(null), 3000)
    }
  }

  const openModal = (petId = null) => {
    if (pets.length === 0) {
      setAlert({ type: 'warning', message: 'Você precisa cadastrar pelo menos um pet antes de adicionar uma tarefa.' })
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
    return pet ? pet.name : 'Pet não encontrado'
  }

  if (loading) {
    return (
      <div className="px-4 py-6">
        <div className="text-center py-12">{MESSAGES.LOADING}</div>
      </div>
    )
  }

  return (
    <div 
      className="px-4 py-6 min-h-screen relative"
      style={{
        backgroundImage: `url(${routineBg})`,
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

        <PageHeader
          title="Rotinas"
          action={() => openModal()}
          actionLabel="Adicionar Tarefa"
          actionClassName="!bg-[#7fa653] hover:!bg-[#6a8a45] text-white"
        />

        {error && (
          <Alert variant="error" className="mb-6">
            {error}
          </Alert>
        )}

        {pets.length === 0 ? (
        <EmptyState
          title="Nenhum pet cadastrado ainda"
          description="Cadastre um pet primeiro para começar a adicionar tarefas à rotina dele"
          icon="🐾"
        />
      ) : (
        <div className="space-y-6">
          {pets.map(pet => {
            const petTasks = routinesByPet[pet.id] || []
            // Show pet even if no tasks, or if it has tasks
            return (
              <Card key={pet.id} className="overflow-hidden">
                <Card.Header className="bg-gray-50 border-b">
                  <div className="flex justify-between items-center">
                    <div>
                      <h2 className="text-2xl font-bold text-gray-900">{pet.name}</h2>
                      <p className="text-sm text-gray-500 mt-1">{pet.species}</p>
                    </div>
                    <Button
                      variant="primary"
                      size="sm"
                      onClick={() => openModal(pet.id)}
                      className="!bg-[#7fa653] hover:!bg-[#6a8a45] text-white"
                    >
                      + Adicionar Tarefa
                    </Button>
                  </div>
                </Card.Header>
                <Card.Body>
                  {petTasks.length === 0 ? (
                    <div className="text-center py-8 text-gray-500">
                      <p>Nenhuma tarefa cadastrada para {pet.name}</p>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => openModal(pet.id)}
                        className="mt-4 !bg-[#cfe0bc] hover:!bg-[#b8d09f] text-gray-800"
                      >
                        Adicionar primeira tarefa
                      </Button>
                    </div>
                  ) : (
                    <div className="space-y-3">
                      {petTasks.map(task => (
                        <div
                          key={task.id}
                          className={`flex justify-between items-start p-4 rounded-lg border ${
                            !task.active ? 'opacity-60 bg-gray-50' : 'bg-white'
                          }`}
                        >
                          <div className="flex-1">
                            <div className="flex items-center space-x-3 mb-2">
                              <h3 className="text-lg font-semibold">{task.type}</h3>
                              <Badge variant={task.active ? 'success' : 'default'}>
                                {task.active ? 'Ativa' : 'Inativa'}
                              </Badge>
                            </div>
                            <div className="space-y-1 text-gray-600">
                              <p>
                                <span className="font-medium">Frequência:</span> {task.frequency}
                              </p>
                              <p>
                                <span className="font-medium">Horário:</span> {task.time}
                              </p>
                            </div>
                          </div>
                          <div className="flex flex-col space-y-2 ml-4">
                            <Button
                              variant={task.active ? 'warning' : 'success'}
                              size="sm"
                              onClick={() => handleToggleActive(task)}
                              className={task.active ? "!bg-[#76bd9b] hover:!bg-[#65a888] text-white" : "!bg-[#7fa653] hover:!bg-[#6a8a45] text-white"}
                            >
                              {task.active ? 'Desativar' : 'Ativar'}
                            </Button>
                            <Button
                              variant="info"
                              size="sm"
                              onClick={() => handleEdit(task)}
                              className="!bg-[#76bd9b] hover:!bg-[#65a888] text-white"
                            >
                              Editar
                            </Button>
                            <Button
                              variant="danger"
                              size="sm"
                              onClick={() => handleDelete(task.id)}
                              className="!bg-[#cfe0bc] hover:!bg-[#b8d09f] text-gray-800"
                            >
                              Excluir
                            </Button>
                          </div>
                        </div>
                      ))}
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
          title={editingRoutine ? 'Editar Tarefa' : 'Adicionar Tarefa à Rotina'}
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
