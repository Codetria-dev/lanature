import Button from '../ui/Button'

const icons = {
  pets: (
    <svg className="w-16 h-16 mx-auto text-brand-300" fill="currentColor" viewBox="0 0 24 24">
      <path d="M11.5 1.5c.8 0 1.5.7 1.5 1.5 0 .8-.7 1.5-1.5 1.5S10 3.8 10 3c0-.8.7-1.5 1.5-1.5zm-5 2C7.3 3.5 8 4.2 8 5c0 .8-.7 1.5-1.5 1.5S5 5.8 5 5c0-.8.7-1.5 1.5-1.5zm10 0c.8 0 1.5.7 1.5 1.5 0 .8-.7 1.5-1.5 1.5S15 5.8 15 5c0-.8.7-1.5 1.5-1.5zM12 9c1.1 0 2 .9 2 2s-.9 2-2 2-2-.9-2-2 .9-2 2-2zM8 12c0 1.1-.9 2-2 2s-2-.9-2-2 .9-2 2-2 2 .9 2 2zm10 0c0 1.1-.9 2-2 2s-2-.9-2-2 .9-2 2-2 2 .9 2 2zM6.5 15.5c.8 0 1.5.7 1.5 1.5 0 .8-.7 1.5-1.5 1.5S5 17.8 5 17c0-.8.7-1.5 1.5-1.5zm11 0c.8 0 1.5.7 1.5 1.5 0 .8-.7 1.5-1.5 1.5S16 17.8 16 17c0-.8.7-1.5 1.5-1.5zM12 14c1.1 0 2 .9 2 2s-.9 2-2 2-2-.9-2-2 .9-2 2-2z"/>
    </svg>
  ),
  routines: (
    <svg className="w-16 h-16 mx-auto text-brand-300" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth={1.5}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M9 12h3.75M9 15h3.75M9 18h3.75m3 .75H18a2.25 2.25 0 002.25-2.25V6.108c0-1.135-.845-2.098-1.976-2.192a48.424 48.424 0 00-1.123-.08m-5.801 0c-.065.21-.1.433-.1.664 0 .414.336.75.75.75h4.5a.75.75 0 00.75-.75 2.25 2.25 0 00-.1-.664m-5.8 0A2.251 2.251 0 0113.5 2.25H15a2.25 2.25 0 012.15 1.586m-5.8 0c-.376.023-.75.05-1.124.08C9.095 4.01 8.25 4.973 8.25 6.108V8.25m0 0H4.875c-.621 0-1.125.504-1.125 1.125v11.25c0 .621.504 1.125 1.125 1.125h9.75c.621 0 1.125-.504 1.125-1.125V9.375c0-.621-.504-1.125-1.125-1.125H8.25zM6.75 12h.008v.008H6.75V12zm0 3h.008v.008H6.75V15zm0 3h.008v.008H6.75V18z"/>
    </svg>
  ),
  history: (
    <svg className="w-16 h-16 mx-auto text-brand-300" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth={1.5}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M12 6v6h4.5m4.5 0a9 9 0 11-18 0 9 9 0 0118 0z"/>
    </svg>
  ),
  generic: (
    <svg className="w-16 h-16 mx-auto text-brand-300" fill="currentColor" viewBox="0 0 24 24">
      <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>
    </svg>
  ),
}

const EmptyState = ({
  title,
  description,
  action,
  actionLabel,
  icon = 'generic',
  actionClassName = '',
}) => {
  const iconSvg = icons[icon] || icons.generic

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-12 text-center">
      <div className="mb-5">
        {iconSvg}
      </div>
      <h3 className="text-xl font-semibold text-gray-900 mb-2">{title}</h3>
      {description && (
        <p className="text-gray-600 mb-6 max-w-md mx-auto leading-relaxed">{description}</p>
      )}
      {action && actionLabel && (
        <Button onClick={action} className={actionClassName}>{actionLabel}</Button>
      )}
    </div>
  )
}

export default EmptyState
