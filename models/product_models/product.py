from sqlalchemy import Column, Integer, String, DateTime, DECIMAL, ForeignKey
from connectors.db import Base
from datetime import datetime, timezone
from models.product_models.master_category import listcategory

class Product(Base):
    __tablename__ = 'product'
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    name = Column(String(255), nullable=False)
    price = Column(DECIMAL(10, 2), nullable=False)
    stock_qty = Column(Integer, nullable=False)
    category_id = Column(Integer, ForeignKey(listcategory.id), nullable=False)
    description = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, onupdate=datetime.now(timezone.utc))