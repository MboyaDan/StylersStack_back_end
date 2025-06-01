from pydantic import BaseModel
from typing import Optional


class FavoriteCreate(BaseModel):
    product_id: int
    user_uid: str


class FavoriteOut(BaseModel):
    productId: str
    productName: str
    imageUrl: str
    price: float
    userId: str

    class Config:
        from_attributes = True
