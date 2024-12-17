from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Unicode
from app import db
from models.product_models.product import Product
from datetime import datetime, timezone

class ProductImg(db.Model):
    __tablename__ = 'product_imgs'
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    product_id = Column(Integer, ForeignKey(Product.id), nullable=False)
    file_path = Column(String(255), nullable=False)
    file_name = Column(String(255), nullable=False)
    mime_type = Column(String(255), nullable=False)
    img_url = Column(Unicode(255), nullable=False)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, onupdate=datetime.now(timezone.utc))
    
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)