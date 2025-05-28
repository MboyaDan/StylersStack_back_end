from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.schemas.cart_schema import CartCreate, CartItem
from app.crud.cart_crud import (
    add_or_update_cart,
    get_cart_for_user,
    delete_cart_item,
)
from app.dependencies import get_db
from app.utils.firebase_auth import verify_firebase_token

router = APIRouter(prefix="/cart", tags=["Cart"])

@router.post("/", response_model=CartItem, status_code=status.HTTP_201_CREATED)
def add_to_cart(
    cart_body: CartCreate,
    db: Session = Depends(get_db),
    user=Depends(verify_firebase_token),
):
    return add_or_update_cart(db, user["uid"], cart_body)

@router.get("/", response_model=List[CartItem])
def read_my_cart(
    db: Session = Depends(get_db),
    user=Depends(verify_firebase_token),
):
    return get_cart_for_user(db, user["uid"])

@router.delete("/{product_id}", response_model=CartItem)
def remove_from_cart(
    product_id: int,
    db: Session = Depends(get_db),
    user=Depends(verify_firebase_token),
):
    cart = delete_cart_item(db, user["uid"], product_id)
    if not cart:
        raise HTTPException(status_code=404, detail="Cart item not found")
    return cart
