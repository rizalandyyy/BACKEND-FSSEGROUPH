from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, DECIMAL
from connectors.db import Base
from models.user_models.user import User


class DiscountCode(Base):
    __tablename__ = 'discount_code'
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    code = Column(String(255), unique=True, nullable=False)
    discount_value = Column(DECIMAL(10, 2))
    expiration_date = Column(DateTime, nullable=False)
    status = Column(String(255), nullable=True)
    seller_id = Column(Integer, ForeignKey(User.id), nullable=False)
   
    
    def __init__(self, code, discount_value, expiration_date,status, seller_id):
        self.code = code
        self.discount_value = discount_value
        self.expiration_date = expiration_date
        self.status = status
        self.seller_id = seller_id
   

    # @property
    # def status(self):
    #     return self._status

    # @status.setter
    # def status(self, value):
    #     self._status = value
