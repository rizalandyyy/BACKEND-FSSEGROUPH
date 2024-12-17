from sqlalchemy import Column, Integer, DateTime, ForeignKey, DECIMAL, Enum
from app import db
from datetime import datetime, timezone
from models.transaction_models.transaction_detail_customer import TrasactionDetailCustomer
from models.product_models.product import Product
import enum


class StatusEnum(enum.Enum):
    pending = "pending",
    complete = "complete",
    rejected = "rejected"

class TransactionDetailSeller(db.Model):
    __tablename__ = 'order_detail_sellers'
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    order_id = Column(Integer, ForeignKey(TrasactionDetailCustomer.id), nullable=False)
    seller_id = Column(Integer, nullable=False)
    product_id = Column(Integer, ForeignKey(Product.id), nullable=False)
    total_price = Column(DECIMAL(10, 2), nullable=False)
    status = Column(Enum(StatusEnum), nullable=False)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, onupdate=datetime.now(timezone.utc))
    
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)