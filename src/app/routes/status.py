from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.db.session import get_db
from src.core.models.delivery_log import DeliveryLog
from typing import List

router = APIRouter()

@router.get("/delivery/{delivery_id}")
def get_delivery_status(
    delivery_id: str,
    db: Session = Depends(get_db)
):
    attempts = db.query(DeliveryLog).filter(
        DeliveryLog.id == delivery_id
    ).order_by(DeliveryLog.attempt_number).all()
    
    if not attempts:
        raise HTTPException(status_code=404, detail="Delivery not found")
    
    return {
        "delivery_id": delivery_id,
        "attempts": [
            {
                "attempt_number": a.attempt_number,
                "status": a.status,
                "status_code": a.status_code,
                "timestamp": a.created_at.isoformat()
            } for a in attempts
        ]
    }

@router.get("/subscription/{subscription_id}")
def get_subscription_status(
    subscription_id: str,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    attempts = db.query(DeliveryLog).filter(
        DeliveryLog.subscription_id == subscription_id
    ).order_by(DeliveryLog.created_at.desc()).limit(limit).all()
    
    return {
        "subscription_id": subscription_id,
        "recent_attempts": [
            {
                "delivery_id": str(a.id),
                "status": a.status,
                "status_code": a.status_code,
                "timestamp": a.created_at.isoformat()
            } for a in attempts
        ]
    }