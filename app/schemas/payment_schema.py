from pydantic import BaseModel, validator, Field
from typing import Optional
from datetime import datetime
from enum import Enum
import re

class PaymentMethod(str, Enum):
    mpesa = "mpesa"
    stripe = "stripe"
    cod = "cod"

class PaymentCreate(BaseModel):
    order_id: str
    amount: float
    currency: str
    phone_number: Optional[str] = None
    payment_method: PaymentMethod

    @validator("phone_number", always=True)
    def validate_phone_number(cls, v, values):
        method = values.get("payment_method")
        if method == PaymentMethod.mpesa:
            if not v:
                raise ValueError("Phone number is required for Mpesa payments.")
            # Validate Kenyan phone format (e.g., 07XXXXXXXX or 2547XXXXXXXX)
            if not re.fullmatch(r"^(07\d{8}|2547\d{8})$", v):
                raise ValueError("Invalid Kenyan phone number format. Use 07XXXXXXXX or 2547XXXXXXXX.")
        return v

class PaymentResponse(BaseModel):
    id: str
    order_id: str
    user_id: str
    amount: float
    currency: str
    payment_method: PaymentMethod
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
    reason: Optional[str] = None