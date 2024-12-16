from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, String, Unicode
from app import db
from models.user_models.user import User
from datetime import datetime, timezone

class AvatarImg(db.Model):
    __tablename__ = 'avatar_imgs'
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    user_id = Column(Integer, ForeignKey(User.id),unique=True, nullable=False)
    file_path = Column(String(255), nullable=False)
    file_name = Column(String(255), nullable=True)
    mime_type = Column(String(255), nullable=True)
    img_url = Column(Unicode(255), nullable=True)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, onupdate=datetime.now(timezone.utc))
    
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value) 
    
        def allowed_file(name):
            return '.' in name and name.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg'}