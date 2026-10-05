from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import session

from app.core.database import get_db
from app.models import User,Product,Order,OrderITEM

from app.router.auth import get_current_user


router = APIRouter( prefix="/admin", tags=["Admin"])


def require_admin(current_user=Depends(get_current_user)):
    if not current_user.is_admin:raise HTTPException(status_code=403,detail="Admin access required")
    return current_user

# Create product
@router.post("/products", status_code=201)
def create_product(name: str,price: float,description: str | None = None, db: session = Depends(get_db),  admin=Depends(require_admin)):
    if price <= 0:
        raise HTTPException(status_code=422,detail="Price must be greater than 0")

    product = Product(name=name,description=description,price=price)

    db.add(product)
    db.commit()
    db.refresh(product)

    return product

@router.put("/products/{product_id}")
def update_product(product_id: int,name: str,price: float,description: str | None = None,db: session = Depends(get_db),admin=Depends(require_admin)):
    product = db.query(Product).filter(Product.id == product_id).first()

    if not product:
        raise HTTPException(status_code=404,detail="Product not found")

    if price <= 0:
        raise HTTPException(status_code=422,detail="Price must be greater than 0")

    product.name = name
    product.price = price
    product.description = description

    db.commit()
    db.refresh(product)

    return product

@router.delete("/products/{product_id}")
def delete_product(product_id: int,db: session = Depends(get_db),admin=Depends(require_admin)):
    product = db.query(Product).filter(Product.id == product_id).first()

    if not product:
        raise HTTPException(status_code=404,detail="Product not found")

    product.is_active = False

    db.commit()

    return {"message": "Product deleted successfully"}

@router.get("/orders")
def get_all_orders(db: session = Depends(get_db), admin=Depends(require_admin)):
    orders = db.query(Order).all()
    result = []

    for order in orders:
        result.append({
            "order_id": order.id,
            "user_id": order.user_id,
            "total_amount": order.total_amount,
            "status": order.status,
            "created_at": order.created_at
        })

    return {"items": result,"total": len(result)}

@router.get("/dashboard")
def admin_dashboard(db: session = Depends(get_db),admin=Depends(require_admin)):
    total_products = db.query(Product).filter(Product.is_active == True).count()

    total_orders = db.query(Order).count()

    paid_orders = db.query(Order).filter(Order.status == "PAID" ).count()

    total_revenue = db.query(func.coalesce(func.sum(Order.total_amount),0)).filter(Order.status == "PAID").scalar()

    return {
        "total_products": total_products,
        "total_orders": total_orders,
        "paid_orders": paid_orders,
        "total_revenue": total_revenue
    }

@router.get("/reports/most-purchased-products")
def most_purchased_products(db: session = Depends(get_db),admin=Depends(require_admin)):
    results = (
        db.query(
            Product.id,Product.name, func.sum(OrderITEM.quantity).label("total_quantity" )
        )
        .join(
            OrderITEM,OrderITEM.product_id == Product.id
        )
        .join(
            Order,Order.id == OrderITEM.order_id
        )
        .filter(Order.status == "PAID")
        .group_by(Product.id,Product.name)
        .order_by(func.sum(OrderITEM.quantity).desc())
        .all()
    )

    return [
        {
            "product_id": product_id,
            "product_name": product_name,
            "total_quantity": total_quantity
        }
        for product_id, product_name, total_quantity in results
    ]

@router.get("/reports/products-never-purchased")
def products_never_purchased(db: session = Depends(get_db),admin=Depends(require_admin)):
    products = (
        db.query(Product)
        .outerjoin(
            OrderITEM,OrderITEM.product_id == Product.id
        )
        .filter(
            OrderITEM.id == None
        )
        .all()
    )

    return [
        {
            "product_id": product.id,
            "product_name": product.name
        }
        for product in products
    ]

@router.get("/reports/orders-per-user")
def orders_per_user(db: session = Depends(get_db),admin=Depends(require_admin)):
    results = (
        db.query(
            User.id,User.name,User.email,
            func.count(Order.id).label(
                "order_count"
            )
        )
        .outerjoin(
            Order,Order.user_id == User.id
        )
        .group_by(
            User.id,User.name,User.email
        )
        .all()
    )

    return [
        {
            "user_id": user_id,
            "name": name,
            "email": email,
            "order_count": order_count
        }
        for user_id, name, email, order_count in results
    ]