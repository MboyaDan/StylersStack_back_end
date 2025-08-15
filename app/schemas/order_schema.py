from datetime import datetime
from typing import List
from pydantic import BaseModel


class OrderItemCreate(BaseModel):
    product_name: str
    quantity: int
    unit_price: float


class OrderItemOut(BaseModel):
    product_name: str
    quantity: int
    unit_price: float

    class Config:
        orm_mode = True


class OrderCreate(BaseModel):
    total_amount: float
    payment_id: str
    items: List[OrderItemCreate]


class OrderOut(BaseModel):
    id: str
    user_uid: str
    total_amount: float
    status: str
    payment_id: str
    created_at: datetime
    items: List[OrderItemOut]

    class Config:
        orm_mode = True
