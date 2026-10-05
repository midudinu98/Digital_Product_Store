from sqlalchemy import Column,Integer,String,Boolean,DateTime,Float
from sqlalchemy.orm import relationship
from datetime import datetime

from app.core.database import base

class Product(base):

    __tablename__="PRODUCTS"

    id=Column(Integer,primary_key=True,index=True)
    name=Column(String(50),nullable=False)
    price=Column(Float,nullable=False)
    is_admin=Column(Boolean,default=False)
    is_active=Column(Boolean,default=True)
    created_AT=Column(DateTime,default=datetime.utcnow)
    
    cart_items=relationship("CartITEM",back_populates="product")
    order_items=relationship("OrderITEM",back_populates="product")