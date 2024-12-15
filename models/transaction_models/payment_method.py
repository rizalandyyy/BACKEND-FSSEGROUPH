from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum
from app import db
from datetime import datetime, timezone
import enum

class PaymentEnum(enum.Enum):
    creditcard = "creditcard",
    debitcard = "debitcard",
    cashondelivery = "COD"
    
    
class PaymentMethod(db.Model):
    __tablename__ = 'payment_methods'
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    payment_method = Column(Enum(PaymentEnum), nullable=False)
    payment_name = Column(String(255), nullable=False)
    payment_number = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    
def __init__(self, **kwargs):
    for key, value in kwargs.items():
        setattr(self, key, value)
def __repr__(self):
    return f'<PaymentMethod(id={self.id}, payment_method={self.payment_method}, payment_name={self.payment_name}, payment_number={self.payment_number})>'