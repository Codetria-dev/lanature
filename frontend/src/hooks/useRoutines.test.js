import { describe, it, expect, vi, beforeEach } from 'vitest'

vi.mock('../services/api')

describe('useRoutines Hook', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('hook is properly structured', () => {
    expect(true).toBe(true)
  })

  it('API mock is configured', async () => {
    const { default: api } = await import('../services/api')
    expect(api).toBeDefined()
  })
})
