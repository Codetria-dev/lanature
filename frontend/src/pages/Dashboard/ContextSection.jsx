import DashboardPets from './DashboardPets'

export default function ContextSection({ pets }) {
  return (
    <div className="mt-16 pt-8 border-t border-gray-200">
      <DashboardPets pets={pets} />
    </div>
  )
}
