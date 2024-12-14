from sqlalchemy import Column, Integer, String, DateTime
from app import db
from datetime import datetime, timezone

class MasterQuestion(db.Model):
    __tablename__ = 'master_questions'
    
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    question = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, onupdate=datetime.now(timezone.utc))  
    
    def __repr__(self):
        return f'<MasterQuestion(id={self.id}, question={self.question})>'