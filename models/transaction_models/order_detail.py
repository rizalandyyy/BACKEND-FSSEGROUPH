from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, DECIMAL, Enum
from sqlalchemy.orm import relationship
from connectors.db import Base
from datetime import datetime, timezone
from models.user_models.user import User
from models.transaction_models.payment_method import PaymentMethod
import enum


class StatusEnum(enum.Enum):
    pending = "pending",
    complete = "complete",
    failed = "failed"


class OrderDetail(Base):
    __tablename__ = 'order_detail'
    
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    user_id = Column(Integer, ForeignKey(User.id), nullable=False)
    payment_id = Column(Integer, ForeignKey(PaymentMethod.id), nullable=False)
    total_price = Column(DECIMAL(10, 2), nullable=False)
    status = Column(Enum(StatusEnum), nullable=False)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, onupdate=datetime.now(timezone.utc))
