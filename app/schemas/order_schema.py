from pydantic import BaseModel
from typing import List

class OrderItemCreate(BaseModel):
    product_name: str
    quantity: int
    unit_price: float

class OrderCreate(BaseModel):
    total_amount: float
    items: List[OrderItemCreate]
    payment_id: str

class OrderOut(BaseModel):
    id: str
    user_uid: str
    total_amount: float
    status: str
    payment_id: str

    class Config:
        orm_mode = True
