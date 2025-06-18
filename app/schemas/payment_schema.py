from pydantic import BaseModel, validator, Field
from typing import Optional
from datetime import datetime, timezone
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
    payment_method: PaymentMethod
    phone_number: Optional[str] = None
    checkout_request_id: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @validator("phone_number", always=True)
    def validate_phone_number(cls, v, values):
        method = values.get("payment_method")
        if method == PaymentMethod.mpesa:
            if not v:
                raise ValueError("Phone number is required for Mpesa payments.")

            # Normalize input: remove whitespace and leading '+' if present
            v = v.strip().replace(" ", "").replace("+", "")

            # Normalize formats
            if v.startswith("0") and re.fullmatch(r"07\d{8}", v):
                return "254" + v[1:]  # 0712345678 → 254712345678
            elif v.startswith("254") and re.fullmatch(r"2547\d{8}", v):
                return v              # 254712345678 → valid
            elif v.startswith("7") and re.fullmatch(r"7\d{8}", v):
                return "254" + v      # 712345678 → 254712345678

            raise ValueError("Invalid Safaricom phone number format. Use 07XXXXXXXX or 2547XXXXXXXX.")
        
        print(f"Payment method is {method}, phone number validation skipped.")

        print(f"Phone number provided: {v}")
        print (f"Validotor values: {values}")
        

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
