from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from connectors.db import Base
from datetime import datetime, timezone
from models.user_models.user import User
from models.product_models.product import Product

class Cart(Base):
    __tablename__ = 'cart'
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    user_id = Column(Integer, ForeignKey(User.id), nullable=False)
    product_id = Column(Integer, ForeignKey(Product.id), nullable=False)
    quantity = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, onupdate=datetime.now(timezone.utc))