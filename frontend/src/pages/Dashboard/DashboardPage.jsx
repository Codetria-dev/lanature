import { useState, useEffect } from 'react'
import { usePets } from '../../hooks/usePets'
import { useRoutines } from '../../hooks/useRoutines'
import { useLogs } from '../../hooks/useLogs'
import DashboardLayout from './DashboardLayout'
import DashboardSummary from './DashboardSummary'
import FocusSection from './FocusSection'
import ContextSection from './ContextSection'
import DashboardAlert from './DashboardAlert'
import DashboardLoading from './DashboardLoading'

export default function DashboardPage() {
  const { pets, loading: petsLoading } = usePets()
  const { routines, loading: routinesLoading } = useRoutines()
  const { logs, fetchLogs } = useLogs()
  const [alert, setAlert] = useState(null)

  useEffect(() => {
    if (!routinesLoading && routines.length > 0) {
      fetchLogs()
    }
  }, [routinesLoading, routines.length, fetchLogs])

  useEffect(() => {
    if (alert) {
      const timer = setTimeout(() => setAlert(null), 5000)
      return () => clearTimeout(timer)
    }
  }, [alert])

  const loading = petsLoading || routinesLoading

  if (loading) {
    return <DashboardLoading loadingPets={petsLoading} />
  }

  return (
    <DashboardLayout>
      <DashboardAlert alert={alert} onClose={() => setAlert(null)} />
      
      <DashboardSummary
        routines={routines}
        pets={pets}
        logs={logs}
      />
      
      <FocusSection
        routines={routines}
        pets={pets}
        logs={logs}
        onShowAlert={setAlert}
      />

      <ContextSection pets={pets} />
    </DashboardLayout>
  )
}
