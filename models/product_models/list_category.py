from sqlalchemy import Column, Integer, String, DateTime
from app import db
from datetime import datetime, timezone

# list category product
class ListCategory(db.Model):
    __tablename__ = 'categories'
    
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    category = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, onupdate=datetime.now(timezone.utc))
    
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)