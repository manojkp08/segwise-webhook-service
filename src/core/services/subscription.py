from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from src.db.session import get_db
from src.core.models.subscription import Subscription
from src.core.schemas.subscription import SubscriptionCreate, SubscriptionUpdate
import uuid

class SubscriptionService:
    def __init__(self, db: Session = Depends(get_db)):
        self.db = db

    def create(self, subscription: SubscriptionCreate):
        db_subscription = Subscription(
            id=uuid.uuid4(),
            target_url=str(subscription.target_url),  # Convert HttpUrl to string
            secret=subscription.secret,
            event_types=subscription.event_types
        )
        self.db.add(db_subscription)
        self.db.commit()
        self.db.refresh(db_subscription)
        return db_subscription

    def get(self, subscription_id: str):
        return self.db.query(Subscription).filter(Subscription.id == subscription_id).first()

    def update(self, subscription_id: str, subscription: SubscriptionUpdate):
        db_subscription = self.get(subscription_id)
        if not db_subscription:
            raise HTTPException(status_code=404, detail="Subscription not found")
        
        update_data = subscription.dict(exclude_unset=True)
        if 'target_url' in update_data:
            update_data['target_url'] = str(update_data['target_url'])  # Convert if present
        
        for key, value in update_data.items():
            setattr(db_subscription, key, value)
            
        self.db.commit()
        self.db.refresh(db_subscription)
        return db_subscription

    def delete(self, subscription_id: str):
        db_subscription = self.get(subscription_id)
        if not db_subscription:
            raise HTTPException(status_code=404, detail="Subscription not found")
        
        self.db.delete(db_subscription)
        self.db.commit()
        return {"status": "success"}