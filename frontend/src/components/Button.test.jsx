import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import Button from './Button'

describe('Button Component', () => {
  it('renders button with text', () => {
    render(<Button>Click me</Button>)
    expect(screen.getByRole('button', { name: /click me/i })).toBeInTheDocument()
  })

  it('handles click events', async () => {
    const handleClick = vi.fn()
    render(<Button onClick={handleClick}>Click me</Button>)

    const button = screen.getByRole('button')
    await userEvent.click(button)

    expect(handleClick).toHaveBeenCalledOnce()
  })

  it('applies variant classes', () => {
    const { container } = render(<Button variant="primary">Primary</Button>)
    const button = container.querySelector('button')
    expect(button.className).toContain('primary')
  })

  it('shows loading state', () => {
    render(<Button isLoading>Loading</Button>)
    expect(screen.getByRole('button')).toHaveAttribute('disabled')
  })

  it('disables button when disabled prop is true', () => {
    render(<Button disabled>Disabled</Button>)
    expect(screen.getByRole('button')).toBeDisabled()
  })

  it('supports different button types', () => {
    const { container } = render(<Button type="submit">Submit</Button>)
    expect(container.querySelector('button')).toHaveAttribute('type', 'submit')
  })
})
