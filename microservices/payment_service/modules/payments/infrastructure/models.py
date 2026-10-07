import datetime
import uuid

from core.database import Base
from sqlalchemy import JSON, Boolean, Column, DateTime, Float, Integer, String


class PaymentTable(Base):
    __tablename__ = "payments"
    id = Column(Integer, primary_key=True, index=True)
    lesson_id = Column(Integer)
    amount = Column(Float)
    status = Column(String, default="pending")



class OutboxEventTable(Base):
    __tablename__ = "outbox_events"


    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))


    aggregate_type = Column(String, nullable=False)


    aggregate_id = Column(String, nullable=False)


    event_type = Column(String, nullable=False)


    payload = Column(JSON, nullable=False)


    is_processed = Column(Boolean, default=False)


    created_at = Column(DateTime, default=datetime.datetime.utcnow)