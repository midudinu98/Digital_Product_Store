from sqlalchemy import Column,Integer,Float,String,DateTime,ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from app.core.database import base

class Payment(base):
     
     __tablename__="PAYMENTS"
       
     id=Column(Integer,primary_key=True,index=True)
     order_id=Column(Integer,ForeignKey("ORDERS.id"),unique=True,nullable=False)
     stripe_id=Column(String(20),nullable=True)
     stripe_pay_id=Column(String(20),nullable=True)
     amount=Column(Float,nullable=False)
     status=Column(String(20),default="PENDING")
     created_AT=Column(DateTime,default=datetime.utcnow)

     order=relationship("Order",back_populates="payment")

     
