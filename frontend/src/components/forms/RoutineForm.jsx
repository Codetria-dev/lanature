import { useState, useEffect } from 'react'
import Input from '../ui/Input'
import Select from '../ui/Select'
import Button from '../ui/Button'
import { ROUTINE_FREQUENCIES, ROUTINE_FREQUENCY_LABELS } from '../../constants'

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
      newErrors.pet_id = 'Selecione um pet'
    }
    if (!formData.type.trim()) {
      newErrors.type = 'Tipo é obrigatório'
    }
    if (!formData.time) {
      newErrors.time = 'Horário é obrigatório'
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
    label: ROUTINE_FREQUENCY_LABELS[freq],
  }))

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <Select
        label="Pet"
        required
        value={formData.pet_id}
        onChange={(e) => setFormData({ ...formData, pet_id: e.target.value })}
        options={petOptions}
        error={errors.pet_id}
      />

      <Input
        label="Tipo"
        required
        value={formData.type}
        onChange={(e) => setFormData({ ...formData, type: e.target.value })}
        error={errors.type}
        placeholder="Ex: ração, remédio, água"
      />

      <Select
        label="Frequência"
        required
        value={formData.frequency}
        onChange={(e) => setFormData({ ...formData, frequency: e.target.value })}
        options={frequencyOptions}
        error={errors.frequency}
      />

      <Input
        label="Horário"
        type="time"
        required
        value={formData.time}
        onChange={(e) => setFormData({ ...formData, time: e.target.value })}
        error={errors.time}
      />

      <div className="flex items-center">
        <input
          type="checkbox"
          id="active"
          className="mr-2"
          checked={formData.active}
          onChange={(e) => setFormData({ ...formData, active: e.target.checked })}
        />
        <label htmlFor="active" className="text-sm font-medium text-gray-700">
          Rotina ativa
        </label>
      </div>

      <div className="flex space-x-4 pt-4">
        <Button
          type="submit"
          loading={loading}
          className="flex-1 !bg-[#7fa653] hover:!bg-[#6a8a45] text-white"
        >
          {routine ? 'Atualizar' : 'Salvar'}
        </Button>
        <Button
          type="button"
          variant="secondary"
          onClick={onCancel}
          disabled={loading}
          className="flex-1 !bg-[#cfe0bc] hover:!bg-[#b8d09f] text-gray-800"
        >
          Cancelar
        </Button>
      </div>
    </form>
  )
}

export default RoutineForm
