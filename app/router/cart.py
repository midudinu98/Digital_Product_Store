from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import session

from app.core.database import get_db
from app.models import Cart, CartITEM, Product
from app.schemas.cart import CartItemCreate, CartItemUpdate
from app.router.auth import get_current_user


router = APIRouter(prefix="/cart",tags=["Cart"])


# Add product to cart
@router.post("/items")
def add_to_cart(data: CartItemCreate,db: session = Depends(get_db),current_user=Depends(get_current_user)):
    # Check product
    product = db.query(Product).filter(Product.id == data.product_id,Product.is_active == True).first()

    if not product:
        raise HTTPException(status_code=404,detail="Product not found")

    # Find user's cart
    cart = db.query(Cart).filter(Cart.user_id == current_user.id).first()

    # Create cart if it doesn't exist
    if not cart:
        cart = Cart(user_id=current_user.id)
        db.add(cart)
        db.commit()
        db.refresh(cart)

    # Check if product already exists in cart
    cart_item = db.query(CartITEM).filter(CartITEM.cart_id == cart.id,CartITEM.product_id == data.product_id).first()

    if cart_item:
        cart_item.quantity += data.quantity
    else:
        cart_item = CartITEM(cart_id=cart.id,product_id=data.product_id,quantity=data.quantity)
        db.add(cart_item)

    db.commit()
    db.refresh(cart_item)

    return {
        "message": "Product added to cart",
        "item_id": cart_item.id,
        "product_id": cart_item.product_id,
        "quantity": cart_item.quantity
    }

# View cart
@router.get("/")
def get_cart(db: session = Depends(get_db),current_user=Depends(get_current_user)):
    cart = db.query(Cart).filter(Cart.user_id == current_user.id).first()

    if not cart:
        return {"items": [],"total_amount": 0}

    items = []

    for item in cart.items:
        item_total = item.product.price * item.quantity

        items.append({
            "item_id": item.id,
            "product_id": item.product.id,
            "name": item.product.name,
            "price": item.product.price,
            "quantity": item.quantity,
            "item_total": item_total
        })

    total_amount = sum(item["item_total"] for item in items
    )

    return {
        "cart_id": cart.id,
        "items": items,
        "total_amount": total_amount
    }

# Update cart item
@router.put("/items/{item_id}")
def update_cart_item(item_id: int,data: CartItemUpdate,db: session = Depends(get_db),current_user=Depends(get_current_user)):
    cart_item = (db.query(CartITEM).join(Cart).filter(CartITEM.id == item_id,Cart.user_id == current_user.id).first())

    if not cart_item:
        raise HTTPException(status_code=404,detail="Cart item not found")

    cart_item.quantity = data.quantity

    db.commit()

    return {
        "message": "Cart item updated successfully",
        "item_id": cart_item.id,
        "quantity": cart_item.quantity
    }


# Remove one item
@router.delete("/items/{item_id}")
def remove_cart_item(item_id: int,db: session = Depends(get_db),current_user=Depends(get_current_user)):
    cart_item = (db.query(CartITEM).join(Cart).filter(CartITEM.id == item_id,Cart.user_id == current_user.id).first())

    if not cart_item:
        raise HTTPException(status_code=404,detail="Cart item not found")

    db.delete(cart_item)
    db.commit()

    return {"message": "Cart item removed successfully"}


# Clear cart
@router.delete("/")
def clear_cart(db: session = Depends(get_db),current_user=Depends(get_current_user)):
    cart = db.query(Cart).filter(Cart.user_id == current_user.id).first()

    if not cart:
        return {"message": "Cart is already empty"}

    db.query(CartITEM).filter(CartITEM.cart_id == cart.id).delete()

    db.commit()

    return {"message": "Cart cleared successfully"}