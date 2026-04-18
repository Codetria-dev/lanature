from __future__ import annotations

from datetime import datetime, timedelta
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models import (
    BillingEvent,
    SubscriptionPlan,
    SubscriptionStatus,
    User,
    UserSubscription,
)


DEFAULT_PLANS: list[dict] = [
    {
        "code": "free",
        "name": "Free",
        "monthly_price_cents": 0,
        "trial_days": 0,
        "max_pets": 3,
        "max_routines_per_pet": 10,
    },
    {
        "code": "pro",
        "name": "Pro",
        "monthly_price_cents": 2900,
        "trial_days": 14,
        "max_pets": 30,
        "max_routines_per_pet": 100,
    },
]


class BillingService:
    @staticmethod
    def ensure_default_plans(db: Session) -> None:
        existing = {
            p.code: p
            for p in db.query(SubscriptionPlan).filter(
                SubscriptionPlan.code.in_([plan["code"] for plan in DEFAULT_PLANS])
            ).all()
        }
        changed = False
        for plan in DEFAULT_PLANS:
            existing_plan = existing.get(plan["code"])
            if existing_plan:
                continue
            db.add(SubscriptionPlan(**plan))
            changed = True
        if changed:
            db.commit()

    @staticmethod
    def get_plan_by_code(db: Session, plan_code: str) -> SubscriptionPlan:
        plan = db.query(SubscriptionPlan).filter(
            SubscriptionPlan.code == plan_code, SubscriptionPlan.is_active.is_(True)
        ).first()
        if not plan:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plan not found")
        return plan

    @staticmethod
    def get_current_subscription(db: Session, user_id: int) -> Optional[UserSubscription]:
        return (
            db.query(UserSubscription)
            .filter(UserSubscription.user_id == user_id)
            .order_by(UserSubscription.created_at.desc())
            .first()
        )

    @staticmethod
    def ensure_user_subscription(db: Session, user_id: int, plan_code: str = "free") -> UserSubscription:
        BillingService.ensure_default_plans(db)
        current = BillingService.get_current_subscription(db, user_id)
        if current:
            return current

        plan = BillingService.get_plan_by_code(db, plan_code)
        now = datetime.utcnow()
        trial_ends_at = now + timedelta(days=plan.trial_days) if plan.trial_days > 0 else None
        status_value = SubscriptionStatus.TRIALING if trial_ends_at else SubscriptionStatus.ACTIVE
        subscription = UserSubscription(
            user_id=user_id,
            plan_id=plan.id,
            status=status_value,
            current_period_start=now,
            current_period_end=now + timedelta(days=30),
            trial_ends_at=trial_ends_at,
        )
        db.add(subscription)
        db.commit()
        db.refresh(subscription)
        return subscription

    @staticmethod
    def change_plan(db: Session, user: User, plan_code: str) -> UserSubscription:
        BillingService.ensure_default_plans(db)
        current = BillingService.ensure_user_subscription(db, user.id, "free")
        plan = BillingService.get_plan_by_code(db, plan_code)
        if current.plan_id == plan.id:
            return current
        current.plan_id = plan.id
        current.status = SubscriptionStatus.ACTIVE
        current.cancel_at_period_end = False
        current.updated_at = datetime.utcnow()
        db.add(
            BillingEvent(
                subscription_id=current.id,
                event_type="plan_changed",
                payload={"plan_code": plan_code, "changed_by_user_id": user.id},
            )
        )
        db.commit()
        db.refresh(current)
        return current

    @staticmethod
    def cancel_subscription(db: Session, user_id: int) -> UserSubscription:
        current = BillingService.ensure_user_subscription(db, user_id, "free")
        current.cancel_at_period_end = True
        db.add(
            BillingEvent(
                subscription_id=current.id,
                event_type="cancel_requested",
                payload={"cancel_at_period_end": True},
            )
        )
        db.commit()
        db.refresh(current)
        return current

    @staticmethod
    def reactivate_subscription(db: Session, user_id: int) -> UserSubscription:
        current = BillingService.ensure_user_subscription(db, user_id, "free")
        current.cancel_at_period_end = False
        if current.status == SubscriptionStatus.CANCELED:
            current.status = SubscriptionStatus.ACTIVE
        db.add(
            BillingEvent(
                subscription_id=current.id,
                event_type="reactivated",
                payload={"cancel_at_period_end": False},
            )
        )
        db.commit()
        db.refresh(current)
        return current

    @staticmethod
    def register_billing_failure(db: Session, subscription_id: int, payload: dict | None = None) -> None:
        subscription = db.query(UserSubscription).filter(UserSubscription.id == subscription_id).first()
        if not subscription:
            return
        subscription.status = SubscriptionStatus.PAST_DUE
        db.add(BillingEvent(subscription_id=subscription.id, event_type="payment_failed", payload=payload))
        db.commit()

    @staticmethod
    def register_billing_success(db: Session, subscription_id: int, payload: dict | None = None) -> None:
        subscription = db.query(UserSubscription).filter(UserSubscription.id == subscription_id).first()
        if not subscription:
            return
        subscription.status = SubscriptionStatus.ACTIVE
        db.add(BillingEvent(subscription_id=subscription.id, event_type="payment_succeeded", payload=payload))
        db.commit()

    @staticmethod
    def get_limits(db: Session, user_id: int) -> tuple[int, int]:
        current = BillingService.ensure_user_subscription(db, user_id, "free")
        plan = db.query(SubscriptionPlan).filter(SubscriptionPlan.id == current.plan_id).first()
        if not plan:
            return 3, 10
        return plan.max_pets, plan.max_routines_per_pet


billing_service = BillingService()
