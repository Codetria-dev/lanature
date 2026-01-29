import classNames from '../../utils/classNames'

const Alert = ({
  children,
  variant = 'info',
  onClose,
  className = '',
}) => {
  const variants = {
    info: 'bg-blue-50 border-blue-200 text-blue-800',
    success: 'bg-green-50 border-green-200 text-green-800',
    warning: 'bg-amber-50 border-amber-200 text-amber-800',
    error: 'bg-red-50 border-red-200 text-red-800',
  }
  
  return (
    <div className={classNames('border rounded-lg px-4 py-3 shadow-sm', variants[variant], className)}>
      <div className="flex justify-between items-start">
        <div className="flex-1 text-sm font-medium">{children}</div>
        {onClose && (
          <button
            onClick={onClose}
            className="ml-4 text-current opacity-60 hover:opacity-100 transition-opacity duration-150 w-5 h-5 flex items-center justify-center rounded hover:bg-black/5"
            aria-label="Fechar"
          >
            ×
          </button>
        )}
      </div>
    </div>
  )
}

export default Alert
