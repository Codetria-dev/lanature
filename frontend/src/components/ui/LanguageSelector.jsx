import { useState, useEffect } from 'react'
import { getLanguage, setLanguage } from '../../i18n'

export default function LanguageSelector() {
  const [currentLang, setCurrentLang] = useState(getLanguage())

  useEffect(() => {
    setCurrentLang(getLanguage())
  }, [])

  const handleLanguageChange = (lang) => {
    setLanguage(lang)
    setCurrentLang(lang)
    // Force page reload to update all translations
    window.location.reload()
  }

  return (
    <div className="flex items-center space-x-2">
      <button
        onClick={() => handleLanguageChange('en')}
        className={`px-3 py-1.5 text-sm font-medium rounded-md transition-colors ${
          currentLang === 'en'
            ? 'bg-[#7fa653] text-white'
            : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
        }`}
      >
        EN
      </button>
      <button
        onClick={() => handleLanguageChange('pt')}
        className={`px-3 py-1.5 text-sm font-medium rounded-md transition-colors ${
          currentLang === 'pt'
            ? 'bg-[#7fa653] text-white'
            : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
        }`}
      >
        PT
      </button>
    </div>
  )
}
