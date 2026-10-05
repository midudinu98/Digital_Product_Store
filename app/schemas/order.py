from pydantic import BaseModel


class OrderItemResponse(BaseModel):
    product_id: int
    product_name: str
    quantity: int
    price: float
    item_total: float


class OrderResponse(BaseModel):
    id: int
    total_amount: float
    status: str
    items: list[OrderItemResponse]