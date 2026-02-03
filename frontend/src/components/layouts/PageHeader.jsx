import Button from '../ui/Button'

const PageHeader = ({ 
  title, 
  action, 
  actionLabel, 
  actionVariant = 'primary', 
  actionClassName = '',
  isProminent = false 
}) => {
  if (isProminent) {
    return (
      <div className="mb-10">
        <h1 className="text-3xl font-bold text-gray-900 tracking-tight mb-6">{title}</h1>
        {action && (
          <Button 
            variant={actionVariant} 
            onClick={action} 
            size="lg"
            className={`${actionClassName} text-lg px-8 py-4 w-full sm:w-auto`}
          >
            {actionLabel}
          </Button>
        )}
      </div>
    )
  }

  return (
    <div className="mb-10">
      <div className="flex justify-between items-center gap-4">
        <h1 className="text-3xl font-bold text-gray-900 tracking-tight">{title}</h1>
        {action && (
          <Button 
            variant={actionVariant} 
            onClick={action} 
            size="sm"
            className={actionClassName}
          >
            {actionLabel}
          </Button>
        )}
      </div>
    </div>
  )
}

export default PageHeader
