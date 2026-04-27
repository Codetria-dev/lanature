import classNames from '../../utils/classNames'

const Select = ({
  label,
  value,
  onChange,
  options = [],
  required = false,
  error,
  className = '',
  id,
  ...props
}) => {
  const selectId = id || `select-${Math.random().toString(36).substr(2, 9)}`
  const errorId = error ? `${selectId}-error` : undefined

  return (
    <div className="w-full space-y-1.5">
      {label && (
        <label
          htmlFor={selectId}
          className="block text-sm font-medium text-gray-700 tracking-tight"
        >
          {label}
          {required && <span className="text-red-500 ml-1" aria-label="required">*</span>}
        </label>
      )}
      <select
        id={selectId}
        value={value}
        onChange={onChange}
        required={required}
        aria-required={required}
        aria-invalid={error ? 'true' : 'false'}
        aria-describedby={errorId}
        className={classNames(
          'w-full px-3.5 py-2.5 border rounded-lg focus:outline-none focus:ring-2 focus:ring-brand-500 focus:ring-offset-0 transition-all duration-150 text-sm cursor-pointer',
          'appearance-none bg-white bg-[url("data:image/svg+xml,%3Csvg xmlns=\'http://www.w3.org/2000/svg\' fill=\'none\' viewBox=\'0 0 20 20\'%3E%3Cpath stroke=\'%236b7280\' stroke-linecap=\'round\' stroke-linejoin=\'round\' stroke-width=\'1.5\' d=\'M6 8l4 4 4-4\'/%3E%3C/svg%3E")] bg-no-repeat bg-right pr-10',
          error
            ? 'border-red-300 focus:border-red-400 focus:ring-red-400 bg-red-50/50'
            : 'border-gray-300 hover:border-gray-400 focus:border-brand-500',
          className
        )}
        {...props}
      >
        {options.map((option) => (
          <option key={option.value} value={option.value}>
            {option.label}
          </option>
        ))}
      </select>
      {error && (
        <p id={errorId} className="text-sm text-red-600 font-medium mt-1" role="alert">
          {error}
        </p>
      )}
    </div>
  )
}

export default Select
