from sqlalchemy import Column, Integer, DateTime, ForeignKey, DECIMAL
from app import db
from datetime import datetime, timezone 
from models.product_models.product import Product
from models.user_models.user import User
from models.transaction_models.transaction_detail_customer import TrasactionDetailCustomer


class OrderProduct(db.Model):
    __tablename__ = 'order_products'
    
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    order_id = Column(Integer, ForeignKey(TrasactionDetailCustomer.id), nullable=False)
    customer_id = Column(Integer, ForeignKey(User.id), nullable=False)
    product_id = Column(Integer, ForeignKey(Product.id), nullable=False)
    quantity = Column(Integer, nullable=False)
    sum_price = Column(DECIMAL(10, 2), nullable=False)
    seller_id = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, onupdate=datetime.now(timezone.utc))
    
    def __init__(self, **kwargs):
        for key, value in kwargs.items():    
            setattr(self, key, value)