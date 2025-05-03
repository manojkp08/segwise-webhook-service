from sqlalchemy import Column, DateTime, String, Boolean, JSON, func
from sqlalchemy.dialects.postgresql import UUID
import uuid
from src.db.session import Base

class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    target_url = Column(String, nullable=False)
    secret = Column(String)
    event_types = Column(JSON)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())