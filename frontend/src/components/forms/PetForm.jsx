import { useState, useEffect } from 'react'
import Input from '../ui/Input'
import Button from '../ui/Button'

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
      newErrors.name = 'Nome é obrigatório'
    }
    if (!formData.species.trim()) {
      newErrors.species = 'Espécie é obrigatória'
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
        label="Nome"
        required
        value={formData.name}
        onChange={(e) => setFormData({ ...formData, name: e.target.value })}
        error={errors.name}
        placeholder="Nome do pet"
      />

      <Input
        label="Espécie"
        required
        value={formData.species}
        onChange={(e) => setFormData({ ...formData, species: e.target.value })}
        error={errors.species}
        placeholder="Ex: Cachorro, Gato, etc."
      />

      <Input
        label="Data de Nascimento (opcional)"
        type="date"
        value={formData.birth_date}
        onChange={(e) => setFormData({ ...formData, birth_date: e.target.value })}
        error={errors.birth_date}
      />

      <div className="flex space-x-4 pt-4">
        <Button
          type="submit"
          loading={loading}
          className="flex-1 !bg-[#7fa653] hover:!bg-[#6a8a45] text-white"
        >
          {pet ? 'Atualizar' : 'Salvar'}
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

export default PetForm
