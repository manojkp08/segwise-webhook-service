from pydantic import BaseModel, Field
from typing import Dict, Any

class WebhookPayload(BaseModel):
    event: str = Field(..., example="order.created")
    data: Dict[str, Any] = Field(..., example={"order_id": "123", "amount": 100})

class WebhookResponse(BaseModel):
    status: str = Field(..., example="accepted")
    delivery_id: str = Field(..., example="550e8400-e29b-41d4-a716-446655440000")
    subscription_id: str = Field(..., example="550e8400-e29b-41d4-a716-446655440000")