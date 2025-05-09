from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from .category_schema import Category

class ProductBase(BaseModel):
    name: str
    description: Optional[str]
    price: float
    category_id: int
    image_url: Optional[str]

class ProductCreate(ProductBase):
    pass

class Product(ProductBase):
    id: int
    created_at: datetime
    category: Category

    class Config:
        orm_mode = True
