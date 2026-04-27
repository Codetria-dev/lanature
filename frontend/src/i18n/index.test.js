import { describe, it, expect, beforeEach, vi } from 'vitest'
import { t, plural, formatDate, formatDateShort, formatNumber, formatRelativeTime, setLanguage, getLanguage } from './index'

describe('i18n utilities', () => {
  beforeEach(() => {
    // Reset language to English for each test
    setLanguage('en')
  })

  describe('t (translation function)', () => {
    it('returns translation for existing key', () => {
      const result = t('welcome')
      expect(result).toBe('Care for your pets with confidence')
    })

    it('returns fallback for missing key', () => {
      const result = t('nonexistent.key')
      expect(result).toContain('Key')
    })

    it('handles nested keys', () => {
      const result = t('dashboard.title')
      expect(result).toBe('Welcome back')
    })

    it('replaces parameters in translations', () => {
      const result = t('dashboard.summary.lastActivityDate', { date: '2024-01-15' })
      expect(result).toContain('2024-01-15')
    })

    it('handles pluralization with count parameter', () => {
      // Using dashboard.summary.tasksToday which has pluralization
      const zero = t('dashboard.summary.tasksToday', { count: 0 })
      const one = t('dashboard.summary.tasksToday', { count: 1 })
      const many = t('dashboard.summary.tasksToday', { count: 5 })

      expect(zero).toBe('No tasks today')
      expect(one).toBe('task today')
      expect(many).toBe('tasks today')
    })
  })

  describe('plural helper', () => {
    it('returns correct plural form based on count', () => {
      const one = plural('pets.count', 1)
      const many = plural('pets.count', 5)

      expect(one).toBe('pet')
      expect(many).toBe('pets')
    })

    it('handles zero count', () => {
      const zero = plural('pets.count', 0)
      expect(zero).toBe('No pets')
    })
  })

  describe('formatDate', () => {
    it('formats date objects', () => {
      const date = new Date('2024-01-15')
      const formatted = formatDate(date)

      expect(formatted).toContain('2024')
      expect(formatted).toContain('January')
    })

    it('formats date strings', () => {
      const formatted = formatDate('2024-01-15')

      expect(formatted).toContain('2024')
    })

    it('returns empty string for invalid dates', () => {
      expect(formatDate(null)).toBe('')
      expect(formatDate('')).toBe('')
      expect(formatDate('invalid')).toBe('')
    })

    it('accepts custom options', () => {
      const date = new Date('2024-01-15')
      const formatted = formatDate(date, { month: 'short', day: '2-digit' })

      expect(formatted).toMatch(/Jan|15/)
    })
  })

  describe('formatDateShort', () => {
    it('formats date in short format', () => {
      const date = new Date('2024-01-15')
      const formatted = formatDateShort(date)

      expect(formatted).toContain('2024')
      expect(formatted).toMatch(/Jan/)
    })
  })

  describe('formatNumber', () => {
    it('formats numbers with locale', () => {
      const formatted = formatNumber(1234.56)
      expect(formatted).toMatch(/1.*234/)
    })

    it('returns empty string for null/undefined', () => {
      expect(formatNumber(null)).toBe('')
      expect(formatNumber(undefined)).toBe('')
    })

    it('accepts custom options', () => {
      const formatted = formatNumber(1234.56, {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
      })

      expect(formatted).toMatch(/\.56/)
    })
  })

  describe('formatRelativeTime', () => {
    beforeEach(() => {
      vi.useFakeTimers()
      vi.setSystemTime(new Date('2024-01-15T12:00:00Z'))
    })

    afterEach(() => {
      vi.useRealTimers()
    })

    it('returns "just now" for very recent dates', () => {
      const date = new Date('2024-01-15T11:59:50Z')
      expect(formatRelativeTime(date)).toBe('just now')
    })

    it('returns minutes ago for recent dates', () => {
      const date = new Date('2024-01-15T11:45:00Z')
      const result = formatRelativeTime(date)
      expect(result).toContain('minute')
      expect(result).toContain('ago')
    })

    it('returns hours ago for dates within 24 hours', () => {
      const date = new Date('2024-01-15T08:00:00Z')
      const result = formatRelativeTime(date)
      expect(result).toContain('hour')
      expect(result).toContain('ago')
    })

    it('returns days ago for dates within a week', () => {
      const date = new Date('2024-01-12T12:00:00Z')
      const result = formatRelativeTime(date)
      expect(result).toContain('day')
      expect(result).toContain('ago')
    })

    it('returns weeks ago for dates within a month', () => {
      const date = new Date('2024-01-01T12:00:00Z')
      const result = formatRelativeTime(date)
      expect(result).toContain('week')
      expect(result).toContain('ago')
    })

    it('returns months ago for dates within a year', () => {
      const date = new Date('2023-10-15T12:00:00Z')
      const result = formatRelativeTime(date)
      expect(result).toContain('month')
      expect(result).toContain('ago')
    })

    it('returns years ago for older dates', () => {
      const date = new Date('2022-01-15T12:00:00Z')
      const result = formatRelativeTime(date)
      expect(result).toContain('year')
      expect(result).toContain('ago')
    })

    it('handles future dates', () => {
      const date = new Date('2024-01-15T14:00:00Z')
      const result = formatRelativeTime(date)
      expect(result).toContain('in')
    })

    it('returns empty string for invalid dates', () => {
      expect(formatRelativeTime(null)).toBe('')
      expect(formatRelativeTime('')).toBe('')
      expect(formatRelativeTime('invalid')).toBe('')
    })

    it('handles date strings', () => {
      const result = formatRelativeTime('2024-01-15T11:45:00Z')
      expect(result).toContain('minute')
    })
  })

  describe('language management', () => {
    it('sets and gets language', () => {
      setLanguage('en')
      expect(getLanguage()).toBe('en')

      setLanguage('en')
      expect(getLanguage()).toBe('en')
    })

    it('persists language to localStorage', () => {
      setLanguage('en')
      const stored = localStorage.getItem('language')
      expect(stored).toBe('en')
    })

    it('ignores invalid languages', () => {
      setLanguage('en')
      setLanguage('invalid')
      expect(getLanguage()).toBe('en')
    })
  })
})
