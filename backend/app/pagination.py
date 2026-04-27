"""
Pagination utilities for LaNature API - Phase 5 Performance Optimization

Provides pagination helpers for list endpoints to handle large datasets efficiently.

Usage:
    from app.pagination import paginate, PaginationParams

    # In router
    @router.get("/pets")
    def list_pets(
        params: PaginationParams = Depends(),
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
    ):
        query = db.query(Pet).filter(Pet.user_id == current_user.id)
        return paginate(query, params.page, params.limit)
"""

from typing import TypeVar, Generic, List, Optional
from pydantic import BaseModel, Field
from math import ceil
from sqlalchemy.orm import Query

T = TypeVar('T')


class PaginationParams(BaseModel):
    """Query parameters for pagination."""
    page: int = Field(1, ge=0, description="Page number (0 defaults to 1)")
    limit: int = Field(10, ge=1, description="Items per page (capped at 100 automatically)")


class PaginationInfo(BaseModel):
    """Pagination metadata."""
    page: int
    limit: int
    total: int
    pages: int
    has_next: bool
    has_previous: bool


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response wrapper."""
    data: List[T]
    pagination: PaginationInfo


def paginate(query: Query, page: int = 1, limit: int = 10) -> dict:
    """
    Paginate a SQLAlchemy query.

    Args:
        query: SQLAlchemy query object
        page: Page number (1-indexed)
        limit: Items per page

    Returns:
        Dictionary with data and pagination info
    """
    # Ensure valid page number
    page = max(1, page)
    limit = min(limit, 100)  # Cap at 100 items per page

    # Get total count (efficient with database)
    total = query.count()

    # Calculate pagination info
    pages = ceil(total / limit) if limit > 0 else 0
    offset = (page - 1) * limit

    # Fetch page data
    data = query.offset(offset).limit(limit).all()

    # Return with pagination metadata
    return {
        "data": data,
        "pagination": {
            "page": page,
            "limit": limit,
            "total": total,
            "pages": pages,
            "has_next": page < pages,
            "has_previous": page > 1,
        }
    }
