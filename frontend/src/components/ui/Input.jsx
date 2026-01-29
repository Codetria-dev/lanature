import classNames from '../../utils/classNames'

const Input = ({
  label,
  type = 'text',
  value,
  onChange,
  placeholder,
  required = false,
  error,
  className = '',
  ...props
}) => {
  return (
    <div className="w-full space-y-1.5">
      {label && (
        <label className="block text-sm font-medium text-gray-700 tracking-tight">
          {label}
          {required && <span className="text-red-500 ml-1">*</span>}
        </label>
      )}
      <input
        type={type}
        value={value}
        onChange={onChange}
        placeholder={placeholder}
        required={required}
        className={classNames(
          'w-full px-3.5 py-2.5 border rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-0 transition-all duration-150 text-sm',
          'placeholder:text-gray-400',
          error
            ? 'border-red-300 focus:border-red-400 focus:ring-red-400 bg-red-50/50'
            : 'border-gray-300 hover:border-gray-400 focus:border-green-500 bg-white',
          className
        )}
        {...props}
      />
      {error && (
        <p className="text-sm text-red-600 font-medium mt-1">{error}</p>
      )}
    </div>
  )
}

export default Input
