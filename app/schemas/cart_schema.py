from pydantic import BaseModel, Field
from datetime import datetime

class CartBase(BaseModel):
    productId: int  = Field(..., alias="productId")
    quantity:  int  = Field(1)

class CartCreate(CartBase):
    """Payload from Flutter → backend (only productId + qty)."""
    pass

class CartItem(CartBase):
    # nested product info for response
    productName:   str
    productPrice:  float
    productImage:  str
    addedAt:       datetime
    userId:        str

    class Config:
        from_attributes = True
        allow_population_by_field_name = True

class Cart(CartItem):
    id: int
    class Config:
        from_attributes = True
        allow_population_by_field_name = True
