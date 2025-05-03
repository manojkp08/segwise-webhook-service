from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from src.db.session import get_db
from src.core.models.subscription import Subscription
from src.core.models.delivery_log import DeliveryLog
from src.workers.tasks import deliver_webhook
import uuid
import json
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/{subscription_id}")
async def ingest_webhook(
    subscription_id: str,
    request: Request,
    db: Session = Depends(get_db)
):
    try:
        # Debug: Log incoming request
        logger.info(f"Incoming webhook for subscription: {subscription_id}")

        # 1. Check subscription exists
        subscription = db.query(Subscription).filter(Subscription.id == subscription_id).first()
        if not subscription or not subscription.is_active:
            logger.error(f"Subscription not found: {subscription_id}")
            raise HTTPException(status_code=404, detail="Subscription not found or inactive")

        # 2. Parse JSON payload (without signature check)
        try:
            payload = await request.json()
            logger.debug(f"Payload received: {payload}")
        except json.JSONDecodeError:
            logger.error("Invalid JSON payload")
            raise HTTPException(status_code=400, detail="Invalid JSON payload")

        # 3. Queue delivery
        delivery_id = str(uuid.uuid4())
        delivery = DeliveryLog(
            id=delivery_id,
            subscription_id=subscription_id,
            attempt_number=0,  # Will be updated by worker
            request_payload=payload,
            status="queued"  # Initial state
        )
        db.add(delivery)
        db.commit()
        logger.info(f"Queueing delivery {delivery_id} to {subscription.target_url}")
        
        deliver_webhook.delay(str(subscription_id), payload)

        return JSONResponse(
            status_code=202,
            content={
                "status": "accepted",
                "delivery_id": delivery_id,
                "subscription_id": subscription_id
            }
        )

    except Exception as e:
        db.rollback()
        logger.exception("Webhook ingestion failed")
        raise HTTPException(status_code=500, detail=str(e))