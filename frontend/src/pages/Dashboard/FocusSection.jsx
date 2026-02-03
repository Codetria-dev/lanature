import TodayTasksSummary from './TodayTasksSummary'

export default function FocusSection({ routines, pets, logs, onShowAlert }) {
  return (
    <div className="mb-16">
      <TodayTasksSummary
        routines={routines}
        pets={pets}
        logs={logs}
        onShowAlert={onShowAlert}
      />
    </div>
  )
}
