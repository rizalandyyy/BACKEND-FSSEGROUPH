from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey
from app import db
from datetime import datetime, timezone
from models.user_models.user import User
from models.product_models.product import Product

class review(db.Model):
    __tablename__ = 'reviews'
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    user_id = Column(Integer, ForeignKey(User.id), nullable=False)
    product_id = Column(Integer, ForeignKey(Product.id), nullable=False)
    rating = Column(Integer, nullable=False)
    comment = Column(String(20), nullable=False)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, onupdate=datetime.now(timezone.utc))