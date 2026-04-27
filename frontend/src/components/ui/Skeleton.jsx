import classNames from '../../utils/classNames'

const Skeleton = ({
  variant = 'text',
  width,
  height,
  className = '',
  lines = 1,
  rounded = false,
  circle = false
}) => {
  const baseStyles = 'animate-shimmer bg-gradient-to-r from-gray-200 via-gray-100 to-gray-200 bg-[length:200%_100%]'

  const variants = {
    text: 'h-4',
    title: 'h-6 w-64',
    subtitle: 'h-5 w-48',
    avatar: 'rounded-full w-10 h-10',
    card: 'rounded-lg min-h-32',
    button: 'rounded-lg h-10 w-32',
    badge: 'rounded-full h-6 w-16',
    input: 'rounded-lg h-10 w-full',
    image: 'rounded-lg w-full h-48',
    icon: 'rounded w-5 h-5',
    table: 'rounded w-full h-12'
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
            role="status"
            aria-label="Loading..."
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
        circle && 'rounded-full',
        className
      )}
      style={{
        width: width || undefined,
        height: height || undefined
      }}
      role="status"
      aria-label="Loading..."
    />
  )
}

// Composite skeleton components for common patterns
export const SkeletonCard = ({ className = '' }) => (
  <div className={classNames('p-4 border rounded-lg space-y-3', className)}>
    <Skeleton variant="title" />
    <Skeleton variant="text" lines={2} />
    <div className="flex gap-2 mt-4">
      <Skeleton variant="button" width="80px" />
      <Skeleton variant="button" width="80px" />
    </div>
  </div>
)

export const SkeletonTable = ({ rows = 5, columns = 4, className = '' }) => (
  <div className={classNames('space-y-2', className)}>
    <div className="flex gap-4 pb-2 border-b">
      {Array.from({ length: columns }).map((_, i) => (
        <Skeleton key={i} variant="text" width="80px" />
      ))}
    </div>
    {Array.from({ length: rows }).map((_, i) => (
      <div key={i} className="flex gap-4 py-2">
        {Array.from({ length: columns }).map((_, j) => (
          <Skeleton key={j} variant="text" width="80px" />
        ))}
      </div>
    ))}
  </div>
)

export const SkeletonList = ({ items = 3, showAvatar = false, className = '' }) => (
  <div className={classNames('space-y-3', className)}>
    {Array.from({ length: items }).map((_, i) => (
      <div key={i} className="flex gap-3 items-center">
        {showAvatar && <Skeleton variant="avatar" />}
        <div className="flex-1 space-y-2">
          <Skeleton variant="text" width="60%" />
          <Skeleton variant="text" width="40%" />
        </div>
      </div>
    ))}
  </div>
)

export const SkeletonForm = ({ fields = 3, className = '' }) => (
  <div className={classNames('space-y-4', className)}>
    {Array.from({ length: fields }).map((_, i) => (
      <div key={i} className="space-y-1">
        <Skeleton variant="text" width="100px" />
        <Skeleton variant="input" />
      </div>
    ))}
    <Skeleton variant="button" className="mt-6" />
  </div>
)

export default Skeleton
