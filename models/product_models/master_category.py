from sqlalchemy import Column, Integer, String, DateTime
from connectors.db import Base
from datetime import datetime, timezone

# list category product
class listcategory(Base):
    __tablename__ = 'category'
    
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    category = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, onupdate=datetime.now(timezone.utc))