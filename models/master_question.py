from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from connectors.db import Base
from datetime import datetime, timezone

class MasterQuestion(Base):
    __tablename__ = 'master_question'
    
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    question = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, onupdate=datetime.now(timezone.utc))  