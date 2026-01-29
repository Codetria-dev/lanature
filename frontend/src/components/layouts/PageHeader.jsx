import Button from '../ui/Button'

const PageHeader = ({ title, action, actionLabel, actionVariant = 'primary', actionClassName = '' }) => {
  return (
    <div className="flex justify-between items-center mb-8">
      <h1 className="text-3xl font-bold text-gray-900 tracking-tight">{title}</h1>
      {action && (
        <Button variant={actionVariant} onClick={action} className={actionClassName}>
          {actionLabel}
        </Button>
      )}
    </div>
  )
}

export default PageHeader
