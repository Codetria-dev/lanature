import classNames from '../../utils/classNames'

const Card = ({
  children,
  className = '',
  padding = true,
  shadow = true,
  ...props
}) => {
  return (
    <div
      className={classNames(
        'bg-white rounded-xl',
        padding && 'p-6',
        shadow && 'shadow-sm hover:shadow-md transition-shadow duration-200 ease-out',
        className
      )}
      {...props}
    >
      {children}
    </div>
  )
}

Card.Header = ({ children, className = '' }) => (
  <div className={classNames('mb-5', className)}>{children}</div>
)

Card.Body = ({ children, className = '' }) => (
  <div className={classNames('space-y-3', className)}>{children}</div>
)

Card.Footer = ({ children, className = '' }) => (
  <div className={classNames('mt-5 pt-5 border-t border-gray-100', className)}>{children}</div>
)

export default Card
