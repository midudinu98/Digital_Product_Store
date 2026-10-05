from sqlalchemy import Column,Integer,Float,String,DateTime,ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from app.core.database import base

class Order(base):

    __tablename__="ORDERS"

    id=Column(Integer,primary_key=True,index=True)
    user_id=Column(Integer,ForeignKey("USERS.id"),unique=True,nullable=False)
    total_amount=Column(Float,nullable=False)
    status=Column(String(20),default="PENDING")
    created_AT=Column(DateTime,default=datetime.utcnow)

    user=relationship("User",back_populates="orders")
    items=relationship("OrderITEM",back_populates="order",cascade="all,delete-orphan")
    payment=relationship("Payment",back_populates="order",uselist=False,cascade="all,delete-orphan")

class OrderITEM(base):

    __tablename__="ORDER ITEMS"
       
    id=Column(Integer,primary_key=True,index=True)
    order_id=Column(Integer,ForeignKey("ORDERS.id"),unique=True,nullable=False)
    product_id=Column(Integer,ForeignKey("PRODUCTS.id"),unique=True,nullable=False) 
    quantity=Column(Integer,nullable=False)
    price=Column(Float,nullable=False)

    order=relationship("Order",back_populates="items")
    product=relationship("Product",back_populates="order_items")
