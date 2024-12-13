from sqlalchemy import Column, Integer, String, Date, ForeignKey, DECIMAL
from app import db
from models.user_models.user import User


class DiscountCode(db.Model):
    __tablename__ = 'discount_codes'
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    code = Column(String(255), unique=True, nullable=False)
    discount_value = Column(DECIMAL(10, 2))
    expiration_date = Column(Date, nullable=False)
    status = Column(String(255), nullable=True)
    seller_id = Column(Integer, ForeignKey(User.id), nullable=False)
   
    
    def __init__(self, code, discount_value, expiration_date,status, seller_id):
        self.code = code
        self.discount_value = discount_value
        self.expiration_date = expiration_date
        self.status = status
        self.seller_id = seller_id

    def __repr__(self):
        return f'<DiscountCode(id={self.id}, code={self.code}, discount_value={self.discount_value}, expiration_date={self.expiration_date}, status={self.status}, seller_id={self.seller_id})>'
