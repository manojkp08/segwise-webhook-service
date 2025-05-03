from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.db.session import get_db
from src.core.schemas.subscription import SubscriptionCreate, SubscriptionUpdate, Subscription
from src.core.services.subscription import SubscriptionService

router = APIRouter()

@router.post("/", response_model=Subscription)
def create_subscription(
    subscription: SubscriptionCreate,
    service: SubscriptionService = Depends(SubscriptionService)
):
    return service.create(subscription)

@router.get("/{subscription_id}", response_model=Subscription)
def read_subscription(
    subscription_id: str,
    service: SubscriptionService = Depends(SubscriptionService)
):
    subscription = service.get(subscription_id)
    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")
    return subscription

@router.put("/{subscription_id}", response_model=Subscription)
def update_subscription(
    subscription_id: str,
    subscription: SubscriptionUpdate,
    service: SubscriptionService = Depends(SubscriptionService)
):
    return service.update(subscription_id, subscription)

@router.delete("/{subscription_id}")
def delete_subscription(
    subscription_id: str,
    service: SubscriptionService = Depends(SubscriptionService)
):
    return service.delete(subscription_id)