import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import Select from './Select'

describe('Select Component', () => {
  const options = [
    { value: '', label: 'Select...' },
    { value: 'option1', label: 'Option 1' },
    { value: 'option2', label: 'Option 2' },
    { value: 'option3', label: 'Option 3' },
  ]

  it('renders select with label', () => {
    render(<Select label="Choose option" options={options} />)
    expect(screen.getByLabelText(/choose option/i)).toBeInTheDocument()
  })

  it('renders all options', () => {
    render(<Select options={options} />)

    options.forEach(option => {
      expect(screen.getByRole('option', { name: option.label })).toBeInTheDocument()
    })
  })

  it('shows required indicator when required', () => {
    render(<Select label="Required field" required options={options} />)
    const indicator = screen.getByText('*')
    expect(indicator).toHaveAttribute('aria-label', 'required')
  })

  it('handles value changes', async () => {
    const handleChange = vi.fn()
    render(<Select value="" onChange={handleChange} options={options} />)

    const select = screen.getByRole('combobox')
    await userEvent.selectOptions(select, 'option1')

    expect(handleChange).toHaveBeenCalled()
  })

  it('shows selected value', () => {
    render(<Select value="option2" onChange={() => {}} options={options} />)

    const select = screen.getByRole('combobox')
    expect(select.value).toBe('option2')
  })

  it('shows error message when error exists', () => {
    render(<Select error="This field is required" options={options} />)

    expect(screen.getByRole('alert')).toHaveTextContent('This field is required')
  })

  it('sets aria-invalid when error exists', () => {
    render(<Select error="Invalid" options={options} />)

    const select = screen.getByRole('combobox')
    expect(select).toHaveAttribute('aria-invalid', 'true')
  })

  it('sets aria-required when required', () => {
    render(<Select required options={options} />)
    expect(screen.getByRole('combobox')).toHaveAttribute('aria-required', 'true')
  })

  it('links label to select with htmlFor/id', () => {
    render(<Select label="Test Label" id="test-select" options={options} />)

    const label = screen.getByText(/test label/i)
    const select = screen.getByRole('combobox')

    expect(label).toHaveAttribute('for', 'test-select')
    expect(select).toHaveAttribute('id', 'test-select')
  })

  it('generates unique id when not provided', () => {
    const { container } = render(<Select label="Test" options={options} />)
    const select = container.querySelector('select')

    expect(select).toHaveAttribute('id')
    expect(select.id).toMatch(/^select-/)
  })

  it('applies custom className', () => {
    const { container } = render(<Select className="custom-class" options={options} />)
    const wrapper = container.firstChild
    expect(wrapper).toHaveClass('w-full')
  })

  it('links error message with aria-describedby', () => {
    render(<Select id="test-select" error="Error message" options={options} />)

    const select = screen.getByRole('combobox')
    const errorId = select.getAttribute('aria-describedby')

    expect(errorId).toBe('test-select-error')
    expect(screen.getByRole('alert')).toHaveAttribute('id', errorId)
  })

  it('renders with empty options array', () => {
    render(<Select label="Empty" options={[]} />)
    expect(screen.getByLabelText(/empty/i)).toBeInTheDocument()
  })

  it('handles multiple option selections in sequence', async () => {
    const handleChange = vi.fn()
    render(<Select value="" onChange={handleChange} options={options} />)

    const select = screen.getByRole('combobox')

    await userEvent.selectOptions(select, 'option1')
    await userEvent.selectOptions(select, 'option2')
    await userEvent.selectOptions(select, 'option3')

    expect(handleChange).toHaveBeenCalledTimes(3)
  })
})
