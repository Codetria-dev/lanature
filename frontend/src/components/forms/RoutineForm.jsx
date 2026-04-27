import { useState, useEffect } from 'react'
import Input from '../ui/Input'
import Select from '../ui/Select'
import Button from '../ui/Button'
import { ROUTINE_FREQUENCIES } from '../../constants'
import { t } from '../../i18n'

const RoutineForm = ({
  routine = null,
  pets = [],
  onSubmit,
  onCancel,
  loading = false,
  defaultPetId = null,
}) => {
  const [formData, setFormData] = useState({
    pet_id: pets.length > 0 ? pets[0].id : '',
    type: '',
    frequency: ROUTINE_FREQUENCIES.DAILY,
    time: '',
    active: true,
  })
  const [errors, setErrors] = useState({})

  useEffect(() => {
    if (routine) {
      setFormData({
        pet_id: routine.pet_id || (pets.length > 0 ? pets[0].id : ''),
        type: routine.type || '',
        frequency: routine.frequency || ROUTINE_FREQUENCIES.DAILY,
        time: routine.time || '',
        active: routine.active !== undefined ? routine.active : true,
      })
    } else if (defaultPetId && pets.find(p => p.id === defaultPetId)) {
      setFormData(prev => ({
        ...prev,
        pet_id: defaultPetId,
      }))
    } else if (pets.length > 0) {
      setFormData(prev => ({
        ...prev,
        pet_id: pets[0].id,
      }))
    }
  }, [routine, pets, defaultPetId])

  const handleSubmit = (e) => {
    e.preventDefault()
    const newErrors = {}

    if (!formData.pet_id) {
      newErrors.pet_id = t('forms.petRequired')
    }
    if (!formData.type.trim()) {
      newErrors.type = t('forms.typeRequired')
    }
    if (!formData.time) {
      newErrors.time = t('forms.timeRequired')
    }

    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors)
      return
    }

    setErrors({})
    onSubmit({
      ...formData,
      pet_id: parseInt(formData.pet_id),
    })
  }

  const petOptions = pets.map(pet => ({
    value: pet.id,
    label: pet.name,
  }))

  const frequencyOptions = Object.values(ROUTINE_FREQUENCIES).map(freq => ({
    value: freq,
    label: t(`frequency.${freq}`),
  }))

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <Select
        label={t('pets.title')}
        required
        value={formData.pet_id}
        onChange={(e) => setFormData({ ...formData, pet_id: e.target.value })}
        options={petOptions}
        error={errors.pet_id}
      />

      <Input
        label={t('routines.type')}
        required
        value={formData.type}
        onChange={(e) => setFormData({ ...formData, type: e.target.value })}
        error={errors.type}
        placeholder={t('forms.typePlaceholder')}
      />

      <Select
        label={t('routines.frequency')}
        required
        value={formData.frequency}
        onChange={(e) => setFormData({ ...formData, frequency: e.target.value })}
        options={frequencyOptions}
        error={errors.frequency}
      />

      <Input
        label={t('routines.time')}
        type="time"
        required
        value={formData.time}
        onChange={(e) => setFormData({ ...formData, time: e.target.value })}
        error={errors.time}
      />

      <div className="flex items-center gap-2">
        <input
          type="checkbox"
          id="active"
          checked={formData.active}
          onChange={(e) => setFormData({ ...formData, active: e.target.checked })}
          className="w-4 h-4 rounded border-gray-300 text-brand-500 focus:ring-brand-500 cursor-pointer transition-all duration-150"
        />
        <label htmlFor="active" className="text-sm font-medium text-gray-700 select-none cursor-pointer">
          {t('forms.activeRoutine')}
        </label>
      </div>

      <div className="flex space-x-4 pt-4">
        <Button
          type="submit"
          loading={loading}
          loadingText={routine ? t('loadingStates.updatingTask') : t('loadingStates.creatingTask')}
          className="flex-1"
        >
          {routine ? t('forms.update') : t('forms.save')}
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

export default RoutineForm
