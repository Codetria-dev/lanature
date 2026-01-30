import { useState, useEffect } from 'react'
import api from '../services/api'

export const usePets = () => {
  const [pets, setPets] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const fetchPets = async () => {
    try {
      setLoading(true)
      setError(null)
      const response = await api.get('/api/v1/pets/')
      setPets(response.data)
    } catch (err) {
      setError(err.response?.data?.detail || 'Error loading pets')
    } finally {
      setLoading(false)
    }
  }

  const createPet = async (petData) => {
    try {
      const response = await api.post('/api/v1/pets/', {
        ...petData,
        birth_date: petData.birth_date || null
      })
      setPets([...pets, response.data])
      return { success: true, data: response.data }
    } catch (err) {
      const errorMsg = err.response?.data?.detail || 'Error creating pet'
      setError(errorMsg)
      return { success: false, error: errorMsg }
    }
  }

  const updatePet = async (id, petData) => {
    try {
      const response = await api.put(`/api/v1/pets/${id}`, petData)
      setPets(pets.map(pet => pet.id === id ? response.data : pet))
      return { success: true, data: response.data }
    } catch (err) {
      const errorMsg = err.response?.data?.detail || 'Error updating pet'
      setError(errorMsg)
      return { success: false, error: errorMsg }
    }
  }

  const deletePet = async (id) => {
    try {
      await api.delete(`/api/v1/pets/${id}`)
      setPets(pets.filter(pet => pet.id !== id))
      return { success: true }
    } catch (err) {
      const errorMsg = err.response?.data?.detail || 'Error deleting pet'
      setError(errorMsg)
      return { success: false, error: errorMsg }
    }
  }

  useEffect(() => {
    fetchPets()
  }, [])

  return {
    pets,
    loading,
    error,
    createPet,
    updatePet,
    deletePet,
  }
}
