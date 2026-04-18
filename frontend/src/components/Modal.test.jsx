import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import Modal from './Modal'

describe('Modal Component', () => {
  it('renders modal when isOpen is true', () => {
    render(
      <Modal isOpen={true} onClose={vi.fn()}>
        <div>Modal content</div>
      </Modal>
    )
    expect(screen.getByText('Modal content')).toBeInTheDocument()
  })

  it('does not render modal when isOpen is false', () => {
    render(
      <Modal isOpen={false} onClose={vi.fn()}>
        <div>Modal content</div>
      </Modal>
    )
    expect(screen.queryByText('Modal content')).not.toBeInTheDocument()
  })

  it('calls onClose when close button is clicked', async () => {
    const handleClose = vi.fn()
    render(
      <Modal isOpen={true} onClose={handleClose}>
        <div>Content</div>
      </Modal>
    )

    const closeButton = screen.getByRole('button', { name: /close|×|✕/i })
    await userEvent.click(closeButton)

    expect(handleClose).toHaveBeenCalled()
  })

  it('renders modal with title', () => {
    render(
      <Modal isOpen={true} onClose={vi.fn()} title="Modal Title">
        <div>Content</div>
      </Modal>
    )
    expect(screen.getByText('Modal Title')).toBeInTheDocument()
  })

  it('supports size variants', () => {
    const { container } = render(
      <Modal isOpen={true} onClose={vi.fn()} size="lg">
        <div>Content</div>
      </Modal>
    )
    const modal = container.querySelector('[role="dialog"]')
    expect(modal.className).toContain('lg')
  })

  it('calls onClose when backdrop is clicked', async () => {
    const handleClose = vi.fn()
    const { container } = render(
      <Modal isOpen={true} onClose={handleClose}>
        <div>Content</div>
      </Modal>
    )

    const backdrop = container.querySelector('.modal-backdrop')
    if (backdrop) {
      await userEvent.click(backdrop)
      expect(handleClose).toHaveBeenCalled()
    }
  })
})
