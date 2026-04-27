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
import { t, formatDate } from '../i18n'
import ListSkeleton from '../components/ui/ListSkeleton'

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
        setAlert({ type: 'success', message: editingPet ? t('pets.petUpdated') : t('pets.petCreated') })
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

  const handleEdit = (pet) => {
    setEditingPet(pet)
    setShowModal(true)
  }

  const handleDelete = async (id) => {
    if (!window.confirm(MESSAGES.CONFIRM_DELETE)) return

    const result = await deletePet(id)
    if (result.success) {
      setAlert({ type: 'success', message: t('pets.petDeleted') })
      setTimeout(() => setAlert(null), 5000)
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
      <div className="px-4 py-6 min-h-screen">
        <div className="container-custom py-8">
          <div className="text-center py-4 text-gray-500 text-sm">
            {t('loadingStates.loadingPets')}
          </div>
          <ListSkeleton count={3} showAvatar={true} showActions={true} />
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

        <PageHeader
          title={t('pets.title')}
          action={openModal}
          actionLabel={t('pets.add')}
          actionClassName="bg-brand-500 hover:bg-brand-600 text-white shadow-md hover:shadow-lg font-semibold"
        />

        {error && (
          <Alert variant="error" className="mb-6">
            {error}
          </Alert>
        )}

        {pets.length === 0 ? (
        <EmptyState
          icon="pets"
          title={t('pets.none')}
          description={t('pets.startAdding')}
          action={openModal}
          actionLabel={t('pets.addFirst')}
          actionClassName="bg-brand-500 hover:bg-brand-600 text-white"
        />
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {pets.map((pet) => {
            return (
              <Card 
                key={pet.id}
              >
                <Card.Header className="pb-4">
                  <div>
                    <h3 className="text-xl font-bold text-gray-900">{pet.name}</h3>
                    <p className="text-sm text-gray-600 mt-1">{pet.species}</p>
                    {pet.birth_date && (
                      <p className="text-xs text-gray-500 mt-2">
                        {t('pets.bornOn')} <span className="font-medium">{formatDate(pet.birth_date)}</span>
                      </p>
                    )}
                  </div>
                </Card.Header>
                <Card.Footer className="pt-4">
                  <div className="flex space-x-2">
                    <Button
                      variant="secondary"
                      size="sm"
                      onClick={() => handleEdit(pet)}
                      className="flex-1"
                    >
                      {t('pets.edit')}
                    </Button>
                    <Button
                      variant="danger"
                      size="sm"
                      onClick={() => handleDelete(pet.id)}
                      className="flex-1"
                    >
                      {t('pets.delete')}
                    </Button>
                  </div>
                </Card.Footer>
              </Card>
            )
          })}
        </div>
        )}

        <Modal
          isOpen={showModal}
          onClose={closeModal}
          title={editingPet ? t('pets.edit') : t('pets.newPet')}
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
