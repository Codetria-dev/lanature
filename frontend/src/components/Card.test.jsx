import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import Card from './ui/Card'

describe('Card Component', () => {
  it('renders card with children', () => {
    render(
      <Card>
        <div>Card content</div>
      </Card>
    )
    expect(screen.getByText('Card content')).toBeInTheDocument()
  })

  it('renders with header', () => {
    render(
      <Card>
        <Card.Header>Header Title</Card.Header>
        <div>Content</div>
      </Card>
    )
    expect(screen.getByText('Header Title')).toBeInTheDocument()
  })

  it('renders with body', () => {
    render(
      <Card>
        <Card.Body>Body content</Card.Body>
      </Card>
    )
    expect(screen.getByText('Body content')).toBeInTheDocument()
  })

  it('renders with footer', () => {
    render(
      <Card>
        <Card.Footer>Footer content</Card.Footer>
      </Card>
    )
    expect(screen.getByText('Footer content')).toBeInTheDocument()
  })

  it('combines header, body, and footer', () => {
    render(
      <Card>
        <Card.Header>Title</Card.Header>
        <Card.Body>Body</Card.Body>
        <Card.Footer>Footer</Card.Footer>
      </Card>
    )
    expect(screen.getByText('Title')).toBeInTheDocument()
    expect(screen.getByText('Body')).toBeInTheDocument()
    expect(screen.getByText('Footer')).toBeInTheDocument()
  })

  it('applies custom className', () => {
    const { container } = render(
      <Card className="custom-class">
        <div>Content</div>
      </Card>
    )
    const card = container.firstChild
    expect(card.className).toContain('custom-class')
  })
})
