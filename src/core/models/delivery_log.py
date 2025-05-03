import uuid
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from src.db.session import Base

class DeliveryLog(Base):
    __tablename__ = "delivery_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    subscription_id = Column(UUID(as_uuid=True), ForeignKey("subscriptions.id"))
    attempt_number = Column(Integer, nullable=False)
    status_code = Column(Integer)
    status = Column(String, nullable=False)  # "success", "failed", "retrying"
    error = Column(String)
    request_payload = Column(JSONB)
    response_payload = Column(JSONB)
    created_at = Column(DateTime(timezone=True), server_default=func.now())