from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import session

from app.core.database import get_db
from app.models import Cart,CartITEM,Order,OrderITEM,Payment

from app.router.auth import get_current_user


router = APIRouter(prefix="/orders",tags=["Orders"])


# Create Order
@router.post("/")
def create_order(db: session = Depends(get_db),current_user=Depends(get_current_user)):
    # Find user's cart
    cart = db.query(Cart).filter(Cart.user_id == current_user.id).first()

    if not cart or not cart.items:
        raise HTTPException(status_code=400,detail="Cart is empty")

    # Calculate total
    total_amount = 0

    for item in cart.items:
        if not item.product.is_active:
            raise HTTPException(status_code=400,detail=f"Product {item.product.name} is not available")

        total_amount += item.product.price * item.quantity

    # Create order
    order = Order(user_id=current_user.id,total_amount=total_amount,status="PENDING")

    db.add(order)
    db.commit()
    db.refresh(order)

    # Create order items
    for item in cart.items:
        order_item = OrderITEM(order_id=order.id,product_id=item.product_id,quantity=item.quantity,price=item.product.price)

        db.add(order_item)

    # Create payment record
    payment = Payment(order_id=order.id,amount=total_amount,status="PENDING")

    db.add(payment)

    # Clear cart
    db.query(CartITEM).filter(CartITEM.cart_id == cart.id).delete()

    db.commit()

    return {
        "message": "Order created successfully",
        "order_id": order.id,
        "total_amount": total_amount,
        "status": order.status
    }


# Get My Orders
@router.get("/")
def get_orders(page: int = 1,limit: int = 10,db: session = Depends(get_db),current_user=Depends(get_current_user)):
    if page < 1:
        raise HTTPException(status_code=400,detail="Page must be greater than 0")

    if limit < 1:
        raise HTTPException(status_code=400,detail="Limit must be greater than 0")

    query = db.query(Order).filter(Order.user_id == current_user.id)

    total = query.count()

    orders = query.offset((page - 1) * limit).limit(limit).all()

    total_pages = (total + limit - 1) // limit

    result = []

    for order in orders:
        result.append({
            "id": order.id,
            "total_amount": order.total_amount,
            "status": order.status,
            "created_at": order.created_at
        })

    return {
        "items": result,
        "page": page,
        "limit": limit,
        "total": total,
        "total_pages": total_pages
    }


# Get One Order
@router.get("/{order_id}")
def get_order(order_id: int,db: session = Depends(get_db),current_user=Depends(get_current_user)):
    order = db.query(Order).filter(Order.id == order_id,Order.user_id == current_user.id).first()

    if not order:
        raise HTTPException(status_code=404,detail="Order not found")

    items = []

    for item in order.items:
        items.append({
            "product_id": item.product_id,
            "product_name": item.product.name,
            "quantity": item.quantity,
            "price": item.price,
            "item_total": item.price * item.quantity
        })

    return {
        "id": order.id,
        "total_amount": order.total_amount,
        "status": order.status,
        "created_at": order.created_at,
        "items": items,
        "payment_status": (
            order.payment.status
            if order.payment
            else "PENDING"
        )
    }