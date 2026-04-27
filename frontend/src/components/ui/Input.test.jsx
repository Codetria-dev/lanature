import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import Input from './Input'

describe('Input Component', () => {
  it('renders input with label', () => {
    render(<Input label="Email" />)
    expect(screen.getByLabelText(/email/i)).toBeInTheDocument()
  })

  it('shows required indicator when required', () => {
    render(<Input label="Email" required />)
    expect(screen.getByLabelText(/required/i)).toBeInTheDocument()
  })

  it('handles value changes', async () => {
    const handleChange = vi.fn()
    render(<Input value="" onChange={handleChange} placeholder="Enter text" />)

    const input = screen.getByPlaceholderText(/enter text/i)
    await userEvent.type(input, 'hello')

    expect(handleChange).toHaveBeenCalled()
  })

  it('shows error message when touched and error exists', async () => {
    const { rerender } = render(
      <Input value="" onChange={() => {}} error="This field is required" />
    )

    // Initially error should not be shown
    expect(screen.queryByRole('alert')).not.toBeInTheDocument()

    // Type to touch the input
    const input = screen.getByRole('textbox')
    await userEvent.type(input, 'a')

    // Now error should be shown
    expect(screen.getByRole('alert')).toHaveTextContent('This field is required')
  })

  it('sets aria-invalid when error exists', async () => {
    render(<Input value="" onChange={() => {}} error="Invalid" />)

    const input = screen.getByRole('textbox')
    await userEvent.type(input, 'a')

    expect(input).toHaveAttribute('aria-invalid', 'true')
  })

  it('sets aria-required when required', () => {
    render(<Input required />)
    expect(screen.getByRole('textbox')).toHaveAttribute('aria-required', 'true')
  })

  it('links label to input with htmlFor/id', () => {
    render(<Input label="Test Label" id="test-input" />)

    const label = screen.getByText(/test label/i)
    const input = screen.getByRole('textbox')

    expect(label).toHaveAttribute('for', 'test-input')
    expect(input).toHaveAttribute('id', 'test-input')
  })

  it('generates unique id when not provided', () => {
    const { container } = render(<Input label="Test" />)
    const input = container.querySelector('input')

    expect(input).toHaveAttribute('id')
    expect(input.id).toMatch(/^input-/)
  })

  it('supports different input types', () => {
    const { container, rerender } = render(<Input type="email" />)
    expect(screen.getByRole('textbox')).toHaveAttribute('type', 'email')

    rerender(<Input type="password" />)
    const passwordInput = container.querySelector('input[type="password"]')
    expect(passwordInput).toHaveAttribute('type', 'password')
  })

  it('applies custom className', () => {
    const { container } = render(<Input className="custom-class" />)
    const input = container.querySelector('input')
    expect(input).toHaveClass('custom-class')
  })
})
