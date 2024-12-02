from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, LargeBinary
from connectors.db import Base
from models.product_models.product import Product
from datetime import datetime, timezone

class ProductImg(Base):
    __tablename__ = 'product_img'
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    product_id = Column(Integer, ForeignKey(Product.id), nullable=False)
    img = Column(LargeBinary, nullable=False)
    name = Column(String(255), nullable=False)
    mime_type = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, onupdate=datetime.now(timezone.utc))