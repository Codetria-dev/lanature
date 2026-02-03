import classNames from '../../utils/classNames'

const Skeleton = ({
  variant = 'text',
  width,
  height,
  className = '',
  lines = 1,
  rounded = false
}) => {
  const baseStyles = 'animate-pulse bg-gray-200'
  
  const variants = {
    text: 'h-4',
    title: 'h-6',
    subtitle: 'h-5',
    avatar: 'rounded-full',
    card: 'rounded-lg',
    button: 'rounded-lg h-10',
    badge: 'rounded-full h-6'
  }
  
  if (lines > 1 && variant === 'text') {
    return (
      <div className={classNames('space-y-2', className)}>
        {Array.from({ length: lines }).map((_, i) => (
          <div
            key={i}
            className={classNames(
              baseStyles,
              variants[variant],
              rounded && 'rounded',
              i === lines - 1 && 'w-3/4' // Last line shorter
            )}
            style={width && i === 0 ? { width } : undefined}
          />
        ))}
      </div>
    )
  }
  
  return (
    <div
      className={classNames(
        baseStyles,
        variants[variant],
        rounded && 'rounded',
        className
      )}
      style={{
        width: width || (variant === 'avatar' ? '40px' : undefined),
        height: height || (variant === 'avatar' ? '40px' : undefined)
      }}
    />
  )
}

export default Skeleton
