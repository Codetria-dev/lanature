import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import Skeleton, { SkeletonCard, SkeletonTable, SkeletonList, SkeletonForm } from './Skeleton'

describe('Skeleton Component', () => {
  it('renders with default variant', () => {
    const { container } = render(<Skeleton />)
    const skeleton = container.firstChild

    expect(skeleton).toBeInTheDocument()
    expect(skeleton).toHaveClass('animate-shimmer')
    expect(skeleton).toHaveAttribute('role', 'status')
    expect(skeleton).toHaveAttribute('aria-label', 'Loading...')
  })

  it('renders different variants correctly', () => {
    const variants = ['text', 'title', 'subtitle', 'avatar', 'card', 'button', 'badge', 'input', 'image', 'icon', 'table']

    variants.forEach(variant => {
      const { container, unmount } = render(<Skeleton variant={variant} />)
      const skeleton = container.firstChild

      expect(skeleton).toHaveClass('animate-shimmer')
      unmount()
    })
  })

  it('renders multiple lines for text variant', () => {
    const { container } = render(<Skeleton variant="text" lines={3} />)
    const skeletons = container.querySelectorAll('.animate-shimmer')

    expect(skeletons).toHaveLength(3)
  })

  it('applies custom width and height', () => {
    const { container } = render(<Skeleton width="200px" height="50px" />)
    const skeleton = container.firstChild

    expect(skeleton).toHaveStyle({ width: '200px', height: '50px' })
  })

  it('applies rounded class when rounded prop is true', () => {
    const { container } = render(<Skeleton rounded />)
    const skeleton = container.firstChild

    expect(skeleton).toHaveClass('rounded')
  })

  it('applies rounded-full class when circle prop is true', () => {
    const { container } = render(<Skeleton circle />)
    const skeleton = container.firstChild

    expect(skeleton).toHaveClass('rounded-full')
  })

  it('applies custom className', () => {
    const { container } = render(<Skeleton className="custom-class" />)
    const skeleton = container.firstChild

    expect(skeleton).toHaveClass('custom-class')
  })

  it('makes last line shorter in multi-line text', () => {
    const { container } = render(<Skeleton variant="text" lines={3} />)
    const skeletons = container.querySelectorAll('.animate-shimmer')
    const lastSkeleton = skeletons[skeletons.length - 1]

    expect(lastSkeleton).toHaveClass('w-3/4')
  })
})

describe('SkeletonCard Component', () => {
  it('renders card skeleton with title, text, and buttons', () => {
    const { container } = render(<SkeletonCard />)

    expect(container.querySelector('.border')).toBeInTheDocument()
    expect(container.querySelectorAll('[role="status"]').length).toBeGreaterThan(0)
  })

  it('applies custom className', () => {
    const { container } = render(<SkeletonCard className="custom-card" />)
    expect(container.firstChild).toHaveClass('custom-card')
  })
})

describe('SkeletonTable Component', () => {
  it('renders table skeleton with default rows and columns', () => {
    const { container } = render(<SkeletonTable />)
    const rows = container.querySelectorAll('.flex.gap-4.py-2')

    expect(rows).toHaveLength(5) // default rows
  })

  it('renders custom number of rows and columns', () => {
    const { container } = render(<SkeletonTable rows={3} columns={6} />)
    const rows = container.querySelectorAll('.flex.gap-4.py-2')

    expect(rows).toHaveLength(3)
  })

  it('applies custom className', () => {
    const { container } = render(<SkeletonTable className="custom-table" />)
    expect(container.firstChild).toHaveClass('custom-table')
  })
})

describe('SkeletonList Component', () => {
  it('renders list skeleton with default items', () => {
    const { container } = render(<SkeletonList />)
    const items = container.querySelectorAll('.flex.gap-3.items-center')

    expect(items).toHaveLength(3) // default items
  })

  it('renders custom number of items', () => {
    const { container } = render(<SkeletonList items={5} />)
    const items = container.querySelectorAll('.flex.gap-3.items-center')

    expect(items).toHaveLength(5)
  })

  it('shows avatars when showAvatar is true', () => {
    const { container } = render(<SkeletonList showAvatar />)
    const avatars = container.querySelectorAll('[role="status"]')

    expect(avatars.length).toBeGreaterThan(3) // includes avatars + text skeletons
  })

  it('does not show avatars by default', () => {
    const { container } = render(<SkeletonList items={1} />)
    const item = container.querySelector('.flex.gap-3.items-center')

    // Should have 2 text skeletons (60% and 40% width), no avatar
    const skeletons = item.querySelectorAll('[role="status"]')
    expect(skeletons).toHaveLength(2)
  })

  it('applies custom className', () => {
    const { container } = render(<SkeletonList className="custom-list" />)
    expect(container.firstChild).toHaveClass('custom-list')
  })
})

describe('SkeletonForm Component', () => {
  it('renders form skeleton with default fields', () => {
    const { container } = render(<SkeletonForm />)
    const fields = container.querySelectorAll('.space-y-1')

    expect(fields).toHaveLength(3) // default fields
  })

  it('renders custom number of fields', () => {
    const { container } = render(<SkeletonForm fields={5} />)
    const fields = container.querySelectorAll('.space-y-1')

    expect(fields).toHaveLength(5)
  })

  it('includes a button skeleton', () => {
    const { container } = render(<SkeletonForm />)
    const button = container.querySelector('.mt-6')

    expect(button).toBeInTheDocument()
  })

  it('applies custom className', () => {
    const { container } = render(<SkeletonForm className="custom-form" />)
    expect(container.firstChild).toHaveClass('custom-form')
  })
})
