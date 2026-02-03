import { useEffect } from 'react'
import Button from './Button'
import { t } from '../../i18n'

const Modal = ({
  isOpen,
  onClose,
  title,
  children,
  footer,
  size = 'md',
}) => {
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden'
    } else {
      document.body.style.overflow = 'unset'
    }
    return () => {
      document.body.style.overflow = 'unset'
    }
  }, [isOpen])

  if (!isOpen) return null

  const sizes = {
    sm: 'max-w-md',
    md: 'max-w-lg',
    lg: 'max-w-2xl',
    xl: 'max-w-4xl',
  }

  return (
    <div 
      className="fixed inset-0 bg-black/40 backdrop-blur-sm flex items-center justify-center z-50 p-4 transition-opacity duration-200"
      onClick={onClose}
      style={{ animation: 'fadeIn 0.2s ease-out' }}
    >
      <div 
        className={`bg-white rounded-xl w-full ${sizes[size]} max-h-[90vh] flex flex-col shadow-2xl transition-all duration-200`}
        onClick={(e) => e.stopPropagation()}
        style={{ animation: 'zoomIn95 0.2s ease-out' }}
      >
        <div className="flex justify-between items-center p-6 border-b border-gray-100">
          <h2 className="text-xl font-semibold text-gray-900 tracking-tight">{title}</h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 text-2xl leading-none transition-colors duration-150 w-8 h-8 flex items-center justify-center rounded-lg hover:bg-gray-100"
            aria-label={t('common.close')}
          >
            ×
          </button>
        </div>
        <div className="p-6 overflow-y-auto flex-1">
          {children}
        </div>
        {footer && (
          <div className="p-6 border-t border-gray-100 flex justify-end space-x-3">
            {footer}
          </div>
        )}
      </div>
    </div>
  )
}

export default Modal
