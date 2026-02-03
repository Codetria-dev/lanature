import classNames from '../../utils/classNames'
import { t } from '../../i18n'

const Button = ({
  children,
  variant = 'primary',
  size = 'md',
  type = 'button',
  disabled = false,
  loading = false,
  loadingText,
  onClick,
  className = '',
  ...props
}) => {
  const baseStyles = 'font-medium rounded-lg transition-all duration-200 ease-out focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed active:scale-[0.98]'
  
  const variants = {
    primary: 'bg-green-600 hover:bg-green-700 text-white focus:ring-green-500 shadow-sm hover:shadow-md',
    secondary: 'bg-gray-200 hover:bg-gray-300 text-gray-800 focus:ring-gray-400 shadow-sm hover:shadow',
    danger: 'bg-red-600 hover:bg-red-700 text-white focus:ring-red-500 shadow-sm hover:shadow-md',
    warning: 'bg-amber-500 hover:bg-amber-600 text-white focus:ring-amber-400 shadow-sm hover:shadow-md',
    info: 'bg-blue-500 hover:bg-blue-600 text-white focus:ring-blue-400 shadow-sm hover:shadow-md',
    outline: 'border-2 border-green-600 text-green-600 hover:bg-green-50 focus:ring-green-500 hover:border-green-700',
    ghost: 'text-gray-700 hover:bg-gray-100 focus:ring-gray-300 hover:text-gray-900',
  }
  
  const sizes = {
    sm: 'px-3 py-1.5 text-sm leading-tight',
    md: 'px-4 py-2 text-sm leading-tight',
    lg: 'px-6 py-3 text-base leading-tight',
  }
  
  return (
    <button
      type={type}
      disabled={disabled || loading}
      onClick={onClick}
      className={classNames(
        baseStyles,
        variants[variant],
        sizes[size],
        loading && 'opacity-75 cursor-wait',
        className
      )}
      {...props}
    >
      {loading ? (
        <span className="flex items-center gap-2">
          <span className="inline-block w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin"></span>
          {loadingText || t('loadingStates.generic')}
        </span>
      ) : (
        children
      )}
    </button>
  )
}

export default Button
