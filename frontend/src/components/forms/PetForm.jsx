import { useState, useEffect } from 'react'
import Input from '../ui/Input'
import Button from '../ui/Button'
import { t } from '../../i18n'

const PetForm = ({
  pet = null,
  onSubmit,
  onCancel,
  loading = false,
}) => {
  const [formData, setFormData] = useState({
    name: '',
    species: '',
    birth_date: '',
  })
  const [errors, setErrors] = useState({})

  useEffect(() => {
    if (pet) {
      setFormData({
        name: pet.name || '',
        species: pet.species || '',
        birth_date: pet.birth_date || '',
      })
    }
  }, [pet])

  const handleSubmit = (e) => {
    e.preventDefault()
    const newErrors = {}

    if (!formData.name.trim()) {
      newErrors.name = t('forms.petNameRequired')
    }
    if (!formData.species.trim()) {
      newErrors.species = t('forms.speciesRequired')
    }

    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors)
      return
    }

    setErrors({})
    onSubmit(formData)
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <Input
        label={t('name')}
        required
        value={formData.name}
        onChange={(e) => setFormData({ ...formData, name: e.target.value })}
        error={errors.name}
        placeholder={t('forms.petName')}
      />

      <Input
        label={t('pets.species')}
        required
        value={formData.species}
        onChange={(e) => setFormData({ ...formData, species: e.target.value })}
        error={errors.species}
        placeholder={t('forms.speciesPlaceholder')}
      />

      <Input
        label={t('forms.birthDateOptional')}
        type="date"
        value={formData.birth_date}
        onChange={(e) => setFormData({ ...formData, birth_date: e.target.value })}
        error={errors.birth_date}
      />

      <div className="flex space-x-4 pt-4">
        <Button
          type="submit"
          loading={loading}
          loadingText={pet ? t('loadingStates.updatingPet') : t('loadingStates.addingPet')}
          className="flex-1"
        >
          {pet ? t('forms.update') : t('forms.save')}
        </Button>
        <Button
          type="button"
          variant="secondary"
          onClick={onCancel}
          disabled={loading}
          className="flex-1"
        >
          {t('forms.cancel')}
        </Button>
      </div>
    </form>
  )
}

export default PetForm
