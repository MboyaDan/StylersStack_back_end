from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class PaymentCreate(BaseModel):
    order_id: str
    amount: float
    currency: str
    phone_number: Optional[str] = None
    payment_method: str = Field(...,regex="^(mpesa|stripe|cod)$")

class PaymentResponse(BaseModel):
    id: str
    order_id: str
    user_id: str
    amount: float
    currency: str
    payment_method: str
    payment_intent_id: str
    status: str
    created_at: datetime

    class Config:
        orm_mode = True

class PaymentConfirm(BaseModel):
    payment_intent_id: str

class RefundRequest(BaseModel):
    payment_intent_id: str
    amount: float
