from sqlalchemy import Column, Integer, String, DateTime, DECIMAL, ForeignKey, Enum
from connectors.db import Base
from datetime import datetime, timezone
from models.product_models.master_category import listcategory
from models.user_models.user import User
import enum

class StatusProduct(enum.Enum):
    handmade = "handmade"
    secondhand = "secondhand"

class Product(Base):
    __tablename__ = 'product'
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    name = Column(String(255), nullable=False)
    price = Column(DECIMAL(10, 2), nullable=False)
    stock_qty = Column(Integer, nullable=False)
    category_id = Column(Integer, ForeignKey(listcategory.id), nullable=False)
    status = Column(Enum(StatusProduct), nullable=False)
    description = Column(String(255), nullable=False)
    seller_id = Column(Integer, ForeignKey(User.id), nullable=False)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, onupdate=datetime.now(timezone.utc))

def Set_status(self, status):
    if status not in StatusProduct.__members__:
        raise ValueError("invalid status. Must be 'handmade' or 'secondhand'")
    self.status = status
    
