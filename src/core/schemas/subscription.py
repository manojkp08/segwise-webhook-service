from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List
from datetime import datetime
from uuid import UUID

class SubscriptionBase(BaseModel):
    target_url: HttpUrl = Field(..., example="https://example.com/webhooks")
    event_types: Optional[List[str]] = Field(
        None,
        example=["order.created", "payment.success"]
    )

class SubscriptionCreate(SubscriptionBase):
    secret: Optional[str] = Field(
        None,
        example="your-hmac-secret-key",
        min_length=16,
        max_length=64
    )

class SubscriptionUpdate(BaseModel):
    target_url: Optional[HttpUrl] = None
    secret: Optional[str] = None
    event_types: Optional[List[str]] = None
    is_active: Optional[bool] = None

class Subscription(SubscriptionBase):
    id: UUID
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True  # For SQLAlchemy compatibility