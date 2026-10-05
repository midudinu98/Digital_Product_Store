from fastapi import FastAPI

from app.core.database import engine,base
from app.models import User,Product,Cart,CartITEM,Order,OrderITEM,Payment

from app.router.auth import router as auth_aouter
from app.router.product import router as product_router
from app.router.cart import router as cart_router
from app.router.order import router as order_router
from app.router.payment import router as payment_router
from app.router.admin import router as admin_router

base.metadata.create_all(bind=engine)

app=FastAPI(title="Digtal Product Store API ")

app.include_router(auth_aouter)
app.include_router(product_router)
app.include_router(cart_router)
app.include_router(order_router)
app.include_router(payment_router)
app.include_router(admin_router)



@app.get("/")
def home():
    return{"message": "API is RUNNING"}