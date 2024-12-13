from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from app import db
from models.user_models.user import User
from models.user_models.master_question import MasterQuestion
from datetime import datetime, timezone

class SecretQuestion(db.Model):
    __tablename__ = 'secret_questions'
    
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    user_id = Column(Integer, ForeignKey(User.id), nullable=False)
    question_id = Column(Integer, ForeignKey(MasterQuestion.id), nullable=False)
    answer = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, onupdate=datetime.now(timezone.utc))  
    
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    def __repr__(self):
        return f'<SecretQuestion(id={self.id}, user_id={self.user_id}, question_id={self.question_id}, answer={self.answer})>'