import os

from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.auth import get_current_user
from app.database import get_db
from app.models import Pet, Routine, RoutineTask, SubscriptionPlan, User, UserSubscription
from app.schemas import (
    ChangePlanRequest,
    SubscriptionPlanResponse,
    UsageResponse,
    UserSubscriptionResponse,
)
from app.domain.billing_service import billing_service


router = APIRouter()


def verify_webhook_secret(x_webhook_secret: str | None = Header(default=None)) -> None:
    configured = os.getenv("BILLING_WEBHOOK_SECRET")
    if not configured:
        raise HTTPException(status_code=500, detail="Webhook secret is not configured")
    if x_webhook_secret != configured:
        raise HTTPException(status_code=401, detail="Invalid webhook secret")


@router.get("/plans", response_model=List[SubscriptionPlanResponse])
def get_plans(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    billing_service.ensure_default_plans(db)
    return db.query(SubscriptionPlan).filter(SubscriptionPlan.is_active.is_(True)).all()


@router.get("/subscription/me", response_model=UserSubscriptionResponse)
def get_my_subscription(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return billing_service.ensure_user_subscription(db, current_user.id, "free")


@router.post("/subscription/change", response_model=UserSubscriptionResponse)
def change_plan(
    payload: ChangePlanRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return billing_service.change_plan(db, current_user, payload.plan_code)


@router.post("/subscription/cancel", response_model=UserSubscriptionResponse)
def cancel_subscription(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return billing_service.cancel_subscription(db, current_user.id)


@router.post("/subscription/reactivate", response_model=UserSubscriptionResponse)
def reactivate_subscription(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return billing_service.reactivate_subscription(db, current_user.id)


@router.get("/usage/me", response_model=UsageResponse)
def get_usage(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    max_pets, max_routines_per_pet = billing_service.get_limits(db, current_user.id)
    pets_count = db.query(Pet).filter(Pet.user_id == current_user.id).count()
    tasks_count = (
        db.query(RoutineTask)
        .join(Routine, RoutineTask.routine_id == Routine.id)
        .join(Pet, Routine.pet_id == Pet.id)
        .filter(Pet.user_id == current_user.id)
        .count()
    )
    return {
        "pets_count": pets_count,
        "tasks_count": tasks_count,
        "max_pets": max_pets,
        "max_routines_per_pet": max_routines_per_pet,
    }


@router.post("/webhooks/internal/payment-failed", status_code=status.HTTP_202_ACCEPTED)
def webhook_payment_failed(
    subscription_id: int,
    _: None = Depends(verify_webhook_secret),
    db: Session = Depends(get_db),
):
    billing_service.register_billing_failure(db, subscription_id, payload={"source": "internal_webhook"})
    return {"status": "accepted"}


@router.post("/webhooks/internal/payment-succeeded", status_code=status.HTTP_202_ACCEPTED)
def webhook_payment_succeeded(
    subscription_id: int,
    _: None = Depends(verify_webhook_secret),
    db: Session = Depends(get_db),
):
    billing_service.register_billing_success(db, subscription_id, payload={"source": "internal_webhook"})
    return {"status": "accepted"}
