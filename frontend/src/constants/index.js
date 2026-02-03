import { t } from '../i18n'

export const ROUTINE_FREQUENCIES = {
  DAILY: 'daily',
  WEEKLY: 'weekly',
  CUSTOM: 'custom'
}

export const LOG_STATUS = {
  DONE: 'done',
  SKIPPED: 'skipped'
}

export const ROUTES = {
  INTRO: '/intro',
  HOME: '/home',
  LOGIN: '/login',
  REGISTER: '/register',
  DASHBOARD: '/dashboard',
  PETS: '/pets',
  ROUTINES: '/routines',
  HISTORY: '/history',
  ADMIN: '/admin',
  CONTACT: '/contact',
  ABOUT: '/about'
}

export const MESSAGES = {
  get LOADING() { return t('messages.loading') },
  get ERROR_GENERIC() { return t('messages.errorGeneric') },
  get CONFIRM_DELETE() { return t('messages.confirmDelete') },
  get SUCCESS_CREATE() { return t('messages.successCreate') },
  get SUCCESS_UPDATE() { return t('messages.successUpdate') },
  get SUCCESS_DELETE() { return t('messages.successDelete') }
}
