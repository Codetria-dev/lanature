import classNames from '../../utils/classNames'

const Badge = ({
  children,
  variant = 'default',
  size = 'md',
  className = '',
}) => {
  const baseStyles = 'inline-flex items-center font-medium rounded-full transition-colors duration-150'
  
  const variants = {
    default: 'bg-gray-100 text-gray-700',
    success: 'bg-green-100 text-green-700',
    danger: 'bg-red-100 text-red-700',
    warning: 'bg-amber-100 text-amber-700',
    info: 'bg-blue-100 text-blue-700',
  }
  
  const sizes = {
    sm: 'px-2 py-0.5 text-xs leading-tight',
    md: 'px-2.5 py-1 text-xs leading-tight',
    lg: 'px-3 py-1.5 text-sm leading-tight',
  }
  
  return (
    <span className={classNames(baseStyles, variants[variant], sizes[size], className)}>
      {children}
    </span>
  )
}

export default Badge
