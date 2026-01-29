// Routine frequencies
export const ROUTINE_FREQUENCIES = {
  DAILY: 'daily',
  WEEKLY: 'weekly',
  CUSTOM: 'custom'
}

export const ROUTINE_FREQUENCY_LABELS = {
  [ROUTINE_FREQUENCIES.DAILY]: 'Daily',
  [ROUTINE_FREQUENCIES.WEEKLY]: 'Weekly',
  [ROUTINE_FREQUENCIES.CUSTOM]: 'Custom'
}

// Log status
export const LOG_STATUS = {
  DONE: 'done',
  SKIPPED: 'skipped'
}

export const LOG_STATUS_LABELS = {
  [LOG_STATUS.DONE]: 'Done',
  [LOG_STATUS.SKIPPED]: 'Skipped'
}

// Routes
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
  CONTACT: '/contact'
}

// Messages
export const MESSAGES = {
  LOADING: 'Carregando...',
  ERROR_GENERIC: 'Ocorreu um erro. Tente novamente.',
  CONFIRM_DELETE: 'Tem certeza que deseja excluir?',
  SUCCESS_CREATE: 'Criado com sucesso!',
  SUCCESS_UPDATE: 'Atualizado com sucesso!',
  SUCCESS_DELETE: 'Excluído com sucesso!'
}
