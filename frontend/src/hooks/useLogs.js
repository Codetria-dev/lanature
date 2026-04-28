import { useState, useEffect } from 'react'
import api from '../services/api'

export const useLogs = (filters = {}) => {
  const [logs, setLogs] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const fetchLogs = async () => {
    try {
      setLoading(true)
      setError(null)

      let url = '/logs/'
      if (filters.petId && filters.petId !== 'all') {
        url = `/logs/pet/${filters.petId}`
      } else if (filters.taskId) {
        url = `/logs/task/${filters.taskId}`
      }

      const response = await api.get(url)
      let filteredLogs = response.data.data || response.data

      if (filters.status && filters.status !== 'all') {
        filteredLogs = filteredLogs.filter(log => log.status === filters.status)
      }

      // Sort by date (most recent first)
      filteredLogs.sort((a, b) => new Date(b.date) - new Date(a.date))

      setLogs(filteredLogs)
    } catch (err) {
      setError(err.response?.data?.detail || 'Error loading history')
    } finally {
      setLoading(false)
    }
  }

  const createLog = async (logData) => {
    try {
      const response = await api.post('/logs/', logData)
      setLogs([response.data, ...logs])
      return { success: true, data: response.data }
    } catch (err) {
      const errorMsg = err.response?.data?.detail || 'Error creating log'
      setError(errorMsg)
      return { success: false, error: errorMsg }
    }
  }

  const updateLog = async (_id, logData) => {
    try {
      // The API upserts logs by (task_id, date) — POST creates or updates
      const response = await api.post('/logs/', {
        task_id: logData.task_id,
        date: logData.date,
        status: logData.status
      })
      // Replace any existing entry with same (task_id, date)
      setLogs(logs.filter(log =>
        !(log.task_id === logData.task_id && log.date === logData.date)
      ).concat([response.data]))
      return { success: true, data: response.data }
    } catch (err) {
      const errorMsg = err.response?.data?.detail || 'Error updating log'
      setError(errorMsg)
      return { success: false, error: errorMsg }
    }
  }

  const deleteLog = async (id) => {
    try {
      await api.delete(`/logs/${id}`)
      setLogs(logs.filter(log => log.id !== id))
      return { success: true }
    } catch (err) {
      const errorMsg = err.response?.data?.detail || 'Error deleting log'
      setError(errorMsg)
      return { success: false, error: errorMsg }
    }
  }

  useEffect(() => {
    fetchLogs()
  }, [filters.petId, filters.taskId, filters.status])

  return {
    logs,
    loading,
    error,
    fetchLogs,
    createLog,
    updateLog,
    deleteLog,
  }
}
