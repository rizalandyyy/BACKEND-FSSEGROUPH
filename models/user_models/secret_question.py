from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from connectors.db import Base
from models.user_models.user import User
from models.user_models.master_question import MasterQuestion
from datetime import datetime, timezone

class SecretQuestion(Base):
    __tablename__ = 'secret_question'
    
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    user_id = Column(Integer, ForeignKey(User.id), nullable=False)
    question_id = Column(Integer, ForeignKey(MasterQuestion.id), nullable=False)
    answer = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, onupdate=datetime.now(timezone.utc))  