from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import session

from app.core.database import get_db
from app.models import Product
from app.schemas.product import ProductCreate,ProductUpdate,ProductResponse

from app.router.auth import get_current_user


router = APIRouter(prefix="/products",tags=["Products"])

@router.post("/", response_model=ProductResponse)
def create_product(product_data: ProductCreate,db: session = Depends(get_db),current_user=Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=403,detail="Admin access required")

    product = Product(name=product_data.name, price=product_data.price)

    db.add(product)
    db.commit()
    db.refresh(product)

    return product

@router.get("/{product_id}", response_model=ProductResponse)
def get_product( product_id: int,db: session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id,Product.is_active == True).first()

    if not product:
        raise HTTPException(status_code=404,detail="Product not found")

    return product


# Get Product by ID
@router.get("/{product_id}", response_model=ProductResponse)
def get_product(product_id: int,db: session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id,Product.is_active == True).first()

    if not product:
        raise HTTPException(status_code=404,detail="Product not found")

    return product

# Get Products + Search + Pagination
@router.get("/")
def get_products(page: int = 1,limit: int = 10,search: str | None = None,db: session = Depends(get_db)):
    if page < 1:
        raise HTTPException(status_code=400,detail="Page must be greater than 0")

    if limit < 1:
        raise HTTPException(status_code=400,detail="Limit must be greater than 0")

    query = db.query(Product).filter(Product.is_active == True)

    # Search
    if search:
        query = query.filter(Product.name.ilike(f"%{search}%"))

    # Total products
    total = query.count()

    # Pagination
    products = query.offset((page - 1) * limit).limit(limit).all()

    # Total pages
    total_pages = (total + limit - 1) // limit

    return {
        "items": products,
        "page": page,
        "limit": limit,
        "total": total,
        "total_pages": total_pages
    }


# Update Product
@router.put("/{product_id}", response_model=ProductResponse)
def update_product(product_id: int,product_data: ProductUpdate,db: session = Depends(get_db),current_user=Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=403,detail="Admin access required")

    product = db.query(Product).filter(Product.id == product_id).first()

    if not product:
        raise HTTPException(status_code=404,detail="Product not found")

    if product_data.name is not None:
        product.name = product_data.name

    if product_data.description is not None:
        product.description = product_data.description

    if product_data.price is not None:
        product.price = product_data.price

    db.commit()
    db.refresh(product)

    return product


# Delete Product
@router.delete("/{product_id}")
def delete_product(product_id: int,db: session = Depends(get_db),current_user=Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=403,detail="Admin access required")

    product = db.query(Product).filter(Product.id == product_id).first()

    if not product:
        raise HTTPException(status_code=404,detail="Product not found")

    # Soft delete
    product.is_active = False

    db.commit()

    return {"message": "Product deleted successfully"}