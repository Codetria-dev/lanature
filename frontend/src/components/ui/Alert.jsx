import classNames from '../../utils/classNames'
import { t } from '../../i18n'

const Alert = ({
  children,
  variant = 'info',
  onClose,
  className = '',
}) => {
  const variants = {
    info: {
      bg: 'bg-blue-50',
      border: 'border-blue-300',
      text: 'text-blue-900',
      icon: 'ℹ️',
      iconBg: 'bg-blue-100'
    },
    success: {
      bg: 'bg-green-50',
      border: 'border-green-400',
      text: 'text-green-900',
      icon: '✓',
      iconBg: 'bg-green-100'
    },
    warning: {
      bg: 'bg-amber-50',
      border: 'border-amber-300',
      text: 'text-amber-900',
      icon: '⚠',
      iconBg: 'bg-amber-100'
    },
    error: {
      bg: 'bg-red-50',
      border: 'border-red-400',
      text: 'text-red-900',
      icon: '✕',
      iconBg: 'bg-red-100'
    },
  }
  
  const variantStyles = variants[variant]
  
  return (
    <div 
      className={classNames(
        'border-2 rounded-lg px-4 py-3 shadow-md animate-slide-down',
        variantStyles.bg,
        variantStyles.border,
        className
      )}
      role="alert"
    >
      <div className="flex items-start gap-3">
        <div className={classNames(
          'flex-shrink-0 w-6 h-6 rounded-full flex items-center justify-center text-sm font-bold',
          variantStyles.iconBg,
          variantStyles.text
        )}>
          {variantStyles.icon}
        </div>
        <div className={classNames('flex-1 text-sm font-semibold', variantStyles.text)}>
          {children}
        </div>
        {onClose && (
          <button
            onClick={onClose}
            className={classNames(
              'flex-shrink-0 text-current opacity-70 hover:opacity-100 transition-opacity duration-150 w-5 h-5 flex items-center justify-center rounded hover:bg-black/10',
              variantStyles.text
            )}
            aria-label={t('common.close')}
          >
            ×
          </button>
        )}
      </div>
    </div>
  )
}

export default Alert
