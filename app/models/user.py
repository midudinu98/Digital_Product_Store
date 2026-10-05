from sqlalchemy import Column,Integer,String,Boolean,DateTime
from sqlalchemy.orm import relationship
from datetime import datetime

from app.core.database import base

class User(base):

    __tablename__="USERS"

    id=Column(Integer,primary_key=True,index=True)
    name=Column(String(50),nullable=False)
    email=Column(String(50),unique=True,nullable=False,index=True)
    password=Column(String(255),nullable=False)
    is_admin=Column(Boolean,default=False)
    created_AT=Column(DateTime,default=datetime.utcnow)

    cart=relationship("Cart",back_populates="user",uselist=False)
    orders=relationship("Order",back_populates="user")