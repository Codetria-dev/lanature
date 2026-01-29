import Button from '../ui/Button'

const EmptyState = ({
  title,
  description,
  action,
  actionLabel,
  icon = '📋',
  actionClassName = '',
}) => {
  return (
    <div className="bg-white rounded-lg shadow p-12 text-center">
      <div className="text-6xl mb-4">{icon}</div>
      <h3 className="text-xl font-semibold text-gray-900 mb-2">{title}</h3>
      {description && (
        <p className="text-gray-500 mb-4">{description}</p>
      )}
      {action && actionLabel && (
        <Button onClick={action} className={actionClassName}>{actionLabel}</Button>
      )}
    </div>
  )
}

export default EmptyState
