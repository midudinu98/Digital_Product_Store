from pydantic import BaseModel, Field


class ProductCreate(BaseModel):
    name: str
    description: str | None = None
    price: float = Field(gt=0)


class ProductUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    price: float | None = Field(default=None, gt=0)


class ProductResponse(BaseModel):
    id: int
    name: str
    description: str | None
    price: float
    is_active: bool

    class Config:
        from_attributes = True