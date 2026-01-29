import { useState } from 'react'
import { usePets } from '../hooks/usePets'
import PageHeader from '../components/layouts/PageHeader'
import EmptyState from '../components/layouts/EmptyState'
import Card from '../components/ui/Card'
import Button from '../components/ui/Button'
import Modal from '../components/ui/Modal'
import PetForm from '../components/forms/PetForm'
import Alert from '../components/ui/Alert'
import { MESSAGES } from '../constants'
import backgroundBg from '@assets/background.png'

export default function Pets() {
  const { pets, loading, error, createPet, updatePet, deletePet } = usePets()
  const [showModal, setShowModal] = useState(false)
  const [editingPet, setEditingPet] = useState(null)
  const [submitLoading, setSubmitLoading] = useState(false)
  const [alert, setAlert] = useState(null)

  const handleSubmit = async (formData) => {
    setSubmitLoading(true)
    try {
      let result
      if (editingPet) {
        result = await updatePet(editingPet.id, formData)
      } else {
        result = await createPet(formData)
      }

      if (result.success) {
        setShowModal(false)
        setEditingPet(null)
        setAlert({ type: 'success', message: editingPet ? 'Pet atualizado com sucesso!' : 'Pet criado com sucesso!' })
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

  const handleEdit = (pet) => {
    setEditingPet(pet)
    setShowModal(true)
  }

  const handleDelete = async (id) => {
    if (!window.confirm(MESSAGES.CONFIRM_DELETE)) return

    const result = await deletePet(id)
    if (result.success) {
      setAlert({ type: 'success', message: 'Pet excluído com sucesso!' })
      setTimeout(() => setAlert(null), 3000)
    } else {
      setAlert({ type: 'error', message: result.error || MESSAGES.ERROR_GENERIC })
    }
  }

  const openModal = () => {
    setEditingPet(null)
    setShowModal(true)
  }

  const closeModal = () => {
    setShowModal(false)
    setEditingPet(null)
  }

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

        <PageHeader
          title="Pets"
          action={openModal}
          actionLabel="Adicionar Pet"
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
          description="Comece adicionando seu primeiro pet"
          action={openModal}
          actionLabel="Adicionar primeiro pet"
          icon="🐾"
          actionClassName="!bg-[#7fa653] hover:!bg-[#6a8a45] text-white"
        />
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {pets.map(pet => (
            <Card key={pet.id} className="card-hover">
              <Card.Header>
                <div className="flex justify-between items-start">
                  <div>
                    <h3 className="text-xl font-semibold">{pet.name}</h3>
                    <p className="text-gray-500 mt-1">{pet.species}</p>
                  </div>
                </div>
                {pet.birth_date && (
                  <p className="text-sm text-gray-400 mt-2">
                    Nascido em: {new Date(pet.birth_date).toLocaleDateString('pt-BR')}
                  </p>
                )}
              </Card.Header>
              <Card.Footer>
                <div className="flex space-x-2">
                  <Button
                    variant="info"
                    size="sm"
                    onClick={() => handleEdit(pet)}
                    className="flex-1 !bg-[#76bd9b] hover:!bg-[#65a888] text-white"
                  >
                    Editar
                  </Button>
                  <Button
                    variant="danger"
                    size="sm"
                    onClick={() => handleDelete(pet.id)}
                    className="flex-1 !bg-[#cfe0bc] hover:!bg-[#b8d09f] text-gray-800"
                  >
                    Excluir
                  </Button>
                </div>
              </Card.Footer>
            </Card>
          ))}
        </div>
        )}

        <Modal
          isOpen={showModal}
          onClose={closeModal}
          title={editingPet ? 'Editar Pet' : 'Novo Pet'}
          size="md"
        >
          <PetForm
            pet={editingPet}
            onSubmit={handleSubmit}
            onCancel={closeModal}
            loading={submitLoading}
          />
        </Modal>
      </div>
    </div>
  )
}
