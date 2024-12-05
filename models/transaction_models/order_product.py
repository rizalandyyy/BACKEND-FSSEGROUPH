from sqlalchemy import Column, Integer, DateTime, ForeignKey, DECIMAL
from sqlalchemy.orm import relationship
from connectors.db import Base
from datetime import datetime, timezone 
from models.transaction_models.order_detail import OrderDetail
from models.product_models.product import Product


class OrderProduct(Base):
    __tablename__ = 'order_product'
    
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    order_id = Column(Integer, ForeignKey(OrderDetail.id), nullable=False)
    product_id = Column(Integer, ForeignKey(Product.id), nullable=False)
    quantity = Column(Integer, nullable=False)
    sum_price = Column(DECIMAL(10, 2), nullable=False)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))