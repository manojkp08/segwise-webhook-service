from celery import Celery
from src.db.session import SessionLocal
from src.core.models.delivery_log import DeliveryLog
from src.core.models.subscription import Subscription
import httpx
import logging

logger = logging.getLogger(__name__)

celery = Celery('tasks', broker='redis://default:MV6QUhIJKDkE1Auf2BYhBQEnP6YzIisv@redis-16388.c279.us-central1-1.gce.redns.redis-cloud.com:16388')

@celery.task(bind=True, max_retries=3)
def deliver_webhook(self, subscription_id: str, payload: dict):
    db = SessionLocal()
    try:    
        # 1. Get subscription
        subscription = db.query(Subscription).get(subscription_id)
        if not subscription:
            logger.error(f"Subscription {subscription_id} not found")
            return

        # 2. Create delivery log
        delivery = DeliveryLog(
            subscription_id=subscription_id,
            attempt_number=self.request.retries + 1,
            request_payload=payload,
            status="processing"
        )
        db.add(delivery)
        db.commit()

        # 3. Send webhook (with timeout)
        response = httpx.post(
            subscription.target_url,
            json=payload,
            timeout=10
        )
        
        # 4. Handle empty responses
        delivery.status_code = response.status_code
        delivery.status = "success" if response.is_success else "failed"
        
        try:
            delivery.response_payload = response.json() if response.content else None
        except ValueError:
            delivery.response_payload = {"raw_response": response.text}
        
        db.commit()
        logger.info(f"Delivered to {subscription.target_url}")

    except httpx.RequestError as e:
        logger.error(f"HTTP error: {str(e)}")
        delivery.status = "failed"
        delivery.error = str(e)
        db.commit()
        raise self.retry(exc=e, countdown=2 ** self.request.retries)
        
    finally:
        db.close()