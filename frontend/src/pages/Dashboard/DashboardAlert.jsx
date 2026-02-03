import Alert from '../../components/ui/Alert'

export default function DashboardAlert({ alert, onClose }) {
  if (!alert) return null

  return (
    <div className="mb-4 fixed top-20 left-1/2 transform -translate-x-1/2 z-50 w-full max-w-2xl px-4">
      <Alert variant={alert.type} onClose={onClose}>
        {alert.message}
      </Alert>
    </div>
  )
}
