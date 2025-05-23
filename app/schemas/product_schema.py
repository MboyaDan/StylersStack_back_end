#Pydantic schema that validates data coming in and formats data going out via the API.
from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime
from .category_schema import Category

class ProductBase(BaseModel):
    name: str
    description: Optional[str]
    price: float
    category_id: int
    images: List[str]
    stock: int
    discount: Optional[float]
    rating: int
    sizes: List[str]
    colors: List[int]

class ProductCreate(ProductBase):
    pass

class Product(ProductBase):
    id: int
    created_at: datetime
    category: Category

    model_config = ConfigDict(from_attributes=True)
