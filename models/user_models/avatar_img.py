from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, String, LargeBinary
from connectors.db import Base
from models.user_models.user import User
from datetime import datetime, timezone

class AvatarImg(Base):
    __tablename__ = 'avatar_img'
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    user_id = Column(Integer, ForeignKey(User.id),unique=True, nullable=False)
    img = Column(LargeBinary, nullable=False)
    name = Column(String(255), nullable=False)
    mime_type = Column(String(50), nullable=False) 
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, onupdate=datetime.now(timezone.utc))
    
    
def allowed_file(name):
    return '.' in name and name.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg'}