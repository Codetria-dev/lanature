import { useState, useEffect } from 'react'
import api from '../services/api'

export const useRoutines = () => {
  const [routines, setRoutines] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const fetchRoutines = async () => {
    try {
      setLoading(true)
      setError(null)
      const response = await api.get('/routines/')
      setRoutines(response.data)
    } catch (err) {
      setError(err.response?.data?.detail || 'Error loading routines')
    } finally {
      setLoading(false)
    }
  }

  const createRoutine = async (routineData) => {
    try {
      const response = await api.post('/routines/', routineData)
      setRoutines([...routines, response.data])
      return { success: true, data: response.data }
    } catch (err) {
      const errorMsg = err.response?.data?.detail || 'Error creating routine'
      setError(errorMsg)
      return { success: false, error: errorMsg }
    }
  }

  const updateRoutine = async (id, routineData) => {
    try {
      const response = await api.put(`/routines/task/${id}`, routineData)
      setRoutines(routines.map(routine => routine.id === id ? response.data : routine))
      return { success: true, data: response.data }
    } catch (err) {
      const errorMsg = err.response?.data?.detail || 'Error updating routine'
      setError(errorMsg)
      return { success: false, error: errorMsg }
    }
  }

  const deleteRoutine = async (id) => {
    try {
      await api.delete(`/routines/task/${id}`)
      setRoutines(routines.filter(routine => routine.id !== id))
      return { success: true }
    } catch (err) {
      const errorMsg = err.response?.data?.detail || 'Error deleting routine'
      setError(errorMsg)
      return { success: false, error: errorMsg }
    }
  }

  const toggleActive = async (routine) => {
    return updateRoutine(routine.id, { ...routine, active: !routine.active })
  }

  useEffect(() => {
    fetchRoutines()
  }, [])

  return {
    routines,
    loading,
    error,
    fetchRoutines,
    createRoutine,
    updateRoutine,
    deleteRoutine,
    toggleActive,
  }
}
