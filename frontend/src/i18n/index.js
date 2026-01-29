import en from './en.json'
import pt from './pt.json'

const translations = {
  en,
  pt
}

let currentLanguage = 'en' // Default to English

export const setLanguage = (lang) => {
  if (translations[lang]) {
    currentLanguage = lang
    localStorage.setItem('language', lang)
  }
}

export const getLanguage = () => {
  const saved = localStorage.getItem('language')
  return saved && translations[saved] ? saved : currentLanguage
}

// Initialize language from localStorage
if (typeof window !== 'undefined') {
  const saved = localStorage.getItem('language')
  if (saved && translations[saved]) {
    currentLanguage = saved
  }
}

export const t = (key, params = {}) => {
  const lang = getLanguage()
  const keys = key.split('.')
  let value = translations[lang]
  
  for (const k of keys) {
    if (value && typeof value === 'object' && k in value) {
      value = value[k]
    } else {
      // Fallback to English if key not found
      value = translations.en
      for (const k2 of keys) {
        if (value && typeof value === 'object' && k2 in value) {
          value = value[k2]
        } else {
          return key // Return key if not found in any language
        }
      }
      break
    }
  }
  
  if (typeof value === 'string' && Object.keys(params).length > 0) {
    return value.replace(/\{\{(\w+)\}\}/g, (match, key) => {
      return params[key] !== undefined ? params[key] : match
    })
  }
  
  return typeof value === 'string' ? value : key
}

export default {
  t,
  setLanguage,
  getLanguage
}
