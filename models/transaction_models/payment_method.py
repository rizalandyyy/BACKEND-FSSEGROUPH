from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum
from connectors.db import Base
from datetime import datetime, timezone
import enum

class PaymentEnum(enum.Enum):
    creditcard = "creditcard",
    debitcard = "debitcard"
    
    
class PaymentMethod(Base):
    __tablename__ = 'payment_method'
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    payment_method = Column(Enum(PaymentEnum), nullable=False)
    payment_name = Column(String(255), nullable=False)
    payment_number = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
  