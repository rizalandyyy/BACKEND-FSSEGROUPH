from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from connectors.db import Base
from datetime import datetime, timezone 
from models.user_models.user import User

class AddressLocation(Base):
    __tablename__ = 'address_location'
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    user_id = Column(Integer, ForeignKey(User.id), nullable=False)
    address = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, onupdate=datetime.now(timezone.utc))