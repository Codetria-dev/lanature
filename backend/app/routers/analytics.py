"""
Analytics API router - Phase 4 Data & Analytics

Exposes usage analytics endpoints for:
- User overview metrics
- Pet-specific analytics
- Historical trends
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any
from app.database import get_db
from app.models import User
from app.auth import get_current_user
from app.domain.analytics_service import analytics_service

router = APIRouter()


@router.get("/overview")
def get_analytics_overview(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get comprehensive overview of user's pet care metrics.

    Returns metrics like:
    - Total pets and routines
    - Today's task completion
    - Overall completion rate
    - Consecutive days streak
    - Most active pet
    - This week's summary

    **Performance:** No caching (real-time calculation)
    """
    return analytics_service.get_overview(current_user.id, db)


@router.get("/pet/{pet_id}")
def get_pet_analytics(
    pet_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get analytics for a specific pet.

    Returns:
    - Total tasks and completion rate
    - Tasks by type breakdown
    - This month's statistics

    **Security:** Only pet owner can view analytics
    """
    result = analytics_service.get_pet_analytics(pet_id, current_user.id, db)
    if not result:
        raise HTTPException(status_code=404, detail="Pet not found")
    return result


@router.get("/history")
def get_analytics_history(
    days: int = 30,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get historical analytics data.

    Returns daily completion data for the past N days and trend analysis.

    **Query Parameters:**
    - days: Number of days to retrieve (default: 30, max: 365)
    """
    if days < 1 or days > 365:
        raise HTTPException(
            status_code=400,
            detail="days must be between 1 and 365"
        )

    return analytics_service.get_history(current_user.id, db, days=days)
