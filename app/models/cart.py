from sqlalchemy import Column,Integer,ForeignKey
from sqlalchemy.orm import relationship

from app.core.database import base

class Cart(base):

    __tablename__="CARTS"

    id=Column(Integer,primary_key=True,index=True)
    user_id=Column(Integer,ForeignKey("USERS.id"),unique=True,nullable=False)

    user=relationship("User",back_populates="cart")
    items=relationship("CartITEM",back_populates="cart",cascade="all,delete-orphan")

class CartITEM(base):

    __tablename__="CARTS ITEMS"

    id=Column(Integer,primary_key=True,index=True)
    cart_id=Column(Integer,ForeignKey("CARTS.id"),unique=True,nullable=False)
    product_id=Column(Integer,ForeignKey("PRODUCTS.id"),unique=True,nullable=False)
    quantity=Column(Integer,nullable=False)

    cart=relationship("Cart",back_populates="items")
    product=relationship("Product",back_populates="cart_items")