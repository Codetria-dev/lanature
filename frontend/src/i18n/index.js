import en from './en.json'
import enUx from './en/ux.json'
import pt from './pt.json'
import ptUx from './pt/ux.json'

// Merge UX copy into main translations
const translations = {
  en: { ...en, ux: enUx },
  pt: { ...pt, ux: ptUx }
}

// Locale mapping
const locales = {
  en: 'en-US',
  pt: 'pt-BR'
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

export const getLocale = () => {
  return locales[getLanguage()] || 'en-US'
}

// Initialize language from localStorage
if (typeof window !== 'undefined') {
  const saved = localStorage.getItem('language')
  if (saved && translations[saved]) {
    currentLanguage = saved
  }
}

// Improved translation function with better fallback
export const t = (key, params = {}) => {
  const lang = getLanguage()
  const keys = key.split('.')
  let value = translations[lang]
  
  // Try to get value from current language
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
          // Elegant fallback: return last key segment instead of full path
          const lastKey = keys[keys.length - 1]
          console.warn(`Translation missing: ${key} (lang: ${lang})`)
          return lastKey.charAt(0).toUpperCase() + lastKey.slice(1).replace(/([A-Z])/g, ' $1').trim()
        }
      }
      break
    }
  }
  
  // Handle pluralization
  if (params.count !== undefined) {
    const count = params.count
    if (typeof value === 'object' && value.zero !== undefined && value.one && value.other) {
      if (count === 0) value = value.zero
      else if (count === 1) value = value.one
      else value = value.other
    } else if (typeof value === 'object' && value.one && value.other) {
      value = count === 1 ? value.one : value.other
    }
  }
  
  if (typeof value === 'string' && Object.keys(params).length > 0) {
    return value.replace(/\{\{(\w+)\}\}/g, (match, key) => {
      return params[key] !== undefined ? params[key] : match
    })
  }
  
  return typeof value === 'string' ? value : (typeof value === 'object' ? key : key)
}

// Pluralization helper
export const plural = (key, count, params = {}) => {
  return t(key, { ...params, count })
}

// Date formatting with locale
export const formatDate = (date, options = {}) => {
  if (!date) return ''
  
  const dateObj = date instanceof Date ? date : new Date(date)
  if (isNaN(dateObj.getTime())) return ''
  
  const locale = getLocale()
  const defaultOptions = {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  }
  
  return dateObj.toLocaleDateString(locale, { ...defaultOptions, ...options })
}

// Short date format (e.g., "Jan 15, 2024" or "15 de jan de 2024")
export const formatDateShort = (date) => {
  return formatDate(date, {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  })
}

// Number formatting with locale
export const formatNumber = (number, options = {}) => {
  if (number === null || number === undefined) return ''
  const locale = getLocale()
  return new Intl.NumberFormat(locale, options).format(number)
}

// Relative time formatting
export const formatRelativeTime = (date) => {
  if (!date) return ''

  const dateObj = date instanceof Date ? date : new Date(date)
  if (isNaN(dateObj.getTime())) return ''

  const now = new Date()
  const diffInSeconds = Math.floor((now - dateObj) / 1000)
  const diffInMinutes = Math.floor(diffInSeconds / 60)
  const diffInHours = Math.floor(diffInMinutes / 60)
  const diffInDays = Math.floor(diffInHours / 24)
  const diffInWeeks = Math.floor(diffInDays / 7)
  const diffInMonths = Math.floor(diffInDays / 30)
  const diffInYears = Math.floor(diffInDays / 365)

  // Future dates
  if (diffInSeconds < 0) {
    const absDiffInSeconds = Math.abs(diffInSeconds)
    const absDiffInMinutes = Math.floor(absDiffInSeconds / 60)
    const absDiffInHours = Math.floor(absDiffInMinutes / 60)
    const absDiffInDays = Math.floor(absDiffInHours / 24)

    if (absDiffInSeconds < 60) {
      return 'in a few seconds'
    } else if (absDiffInMinutes < 60) {
      return `in ${absDiffInMinutes} ${absDiffInMinutes === 1 ? 'minute' : 'minutes'}`
    } else if (absDiffInHours < 24) {
      return `in ${absDiffInHours} ${absDiffInHours === 1 ? 'hour' : 'hours'}`
    } else {
      return `in ${absDiffInDays} ${absDiffInDays === 1 ? 'day' : 'days'}`
    }
  }

  // Past dates
  if (diffInSeconds < 60) {
    return 'just now'
  } else if (diffInMinutes < 60) {
    return `${diffInMinutes} ${diffInMinutes === 1 ? 'minute' : 'minutes'} ago`
  } else if (diffInHours < 24) {
    return `${diffInHours} ${diffInHours === 1 ? 'hour' : 'hours'} ago`
  } else if (diffInDays < 7) {
    return `${diffInDays} ${diffInDays === 1 ? 'day' : 'days'} ago`
  } else if (diffInWeeks < 4) {
    return `${diffInWeeks} ${diffInWeeks === 1 ? 'week' : 'weeks'} ago`
  } else if (diffInMonths < 12) {
    return `${diffInMonths} ${diffInMonths === 1 ? 'month' : 'months'} ago`
  } else {
    return `${diffInYears} ${diffInYears === 1 ? 'year' : 'years'} ago`
  }
}

export default {
  t,
  plural,
  formatDate,
  formatDateShort,
  formatNumber,
  formatRelativeTime,
  setLanguage,
  getLanguage,
  getLocale
}
