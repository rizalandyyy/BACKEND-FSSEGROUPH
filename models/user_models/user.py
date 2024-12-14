from sqlalchemy import Column, Integer, String, DateTime, Enum
from app import db
from datetime import datetime, timezone
from bcrypt import hashpw, gensalt, checkpw
import enum


class Role_division(enum.Enum):
    seller = "Seller"
    customer = "Customer"
    
class Gender(enum.Enum):
    male = "Male"
    female = "Female"
    
class User(db.Model):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    firstName = Column(String(255), nullable=False)
    lastName = Column(String(255), nullable=False)
    gender = Column(Enum(Gender), nullable=False)
    userName = Column(String(255), unique=True, nullable = False)
    email = Column(String(255), unique=True, nullable=False)
    phoneNumber= Column(String(20), nullable=True)
    password = Column(String(255), nullable=False)
    role = Column(Enum(Role_division), nullable=False)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, onupdate=datetime.now(timezone.utc))
    
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    def __repr__(self):
        return f'<User(id={self.id}, userName={self.userName}, email={self.email}, firstName={self.firstName}, lastName={self.lastName}, phoneNumber={self.phoneNumber}>'
    
    def set_password(self, password):
        self.password = hashpw(password.encode('utf-8'), gensalt()).decode('utf-8')

    def check_password(self, password):
        stored_password = self.password.encode('utf-8')
        return checkpw(password.encode('utf-8'), stored_password) if stored_password else False
    
    def set_role(self, role):
        if role not in Role_division.__members__:
            raise ValueError("Invalid role. Must be 'seller' or 'customer'")
        self.role = role
        
    def set_gender(self, gender):
        if gender not in Gender.__members__:
            raise ValueError("Invalid gender. Must be 'male' or 'female'")
        self.gender = gender
        
     