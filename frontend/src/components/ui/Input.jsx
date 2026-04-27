import { useState } from 'react'
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
  id,
  ...props
}) => {
  const [touched, setTouched] = useState(false)
  const inputId = id || `input-${Math.random().toString(36).substr(2, 9)}`
  const errorId = error ? `${inputId}-error` : undefined

  const handleChange = (e) => {
    setTouched(true)
    if (onChange) onChange(e)
  }

  return (
    <div className={classNames('w-full space-y-1.5', error && touched && 'animate-shake')}>
      {label && (
        <label
          htmlFor={inputId}
          className="block text-sm font-medium text-gray-700 tracking-tight"
        >
          {label}
          {required && <span className="text-red-500 ml-1" aria-label="required">*</span>}
        </label>
      )}
      <div className="relative">
        {error && touched && (
          <div className="absolute inset-y-0 left-0 flex items-center pl-3 pointer-events-none">
            <svg className="w-4 h-4 text-red-500" fill="currentColor" viewBox="0 0 20 20" aria-hidden="true">
              <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
            </svg>
          </div>
        )}
        <input
          id={inputId}
          type={type}
          value={value}
          onChange={handleChange}
          placeholder={placeholder}
          required={required}
          aria-required={required}
          aria-invalid={error && touched ? 'true' : 'false'}
          aria-describedby={errorId}
          className={classNames(
            'w-full px-3.5 py-2.5 border rounded-lg focus:outline-none focus:ring-2 focus:ring-brand-500 focus:ring-offset-0 transition-all duration-150 text-sm',
            'placeholder:text-gray-400',
            error && touched
              ? 'border-red-400 focus:border-red-500 focus:ring-red-500 bg-red-50/50 pl-9'
              : 'border-gray-300 hover:border-gray-400 focus:border-brand-500 bg-white',
            className
          )}
          {...props}
        />
      </div>
      {error && touched && (
        <p
          id={errorId}
          className="text-sm text-red-600 font-medium mt-1 flex items-center gap-1.5"
          role="alert"
        >
          <svg className="w-3.5 h-3.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20" aria-hidden="true">
            <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
          </svg>
          {error}
        </p>
      )}
    </div>
  )
}

export default Input
