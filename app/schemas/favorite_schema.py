# favorite_schema.py
from pydantic import BaseModel
from typing import List


class FavoriteOut(BaseModel):
    productId: str
    productName: str
    imageUrl: str
    price: float
    userId: str

    class Config:
        from_attributes = True
