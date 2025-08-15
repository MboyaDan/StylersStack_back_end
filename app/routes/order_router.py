from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.schemas.order_schema import OrderCreate, OrderOut
from app.crud.order_crud import create_order, get_orders_by_user, get_order_by_id
from app.dependencies import get_db
from app.utils.firebase_auth import verify_firebase_token

router = APIRouter(prefix="/orders", tags=["Orders"])

@router.post("/", response_model=OrderOut)
def place_order(
    order_data: OrderCreate,
    db: Session = Depends(get_db),
    user=Depends(verify_firebase_token),
):
    try:
        order = create_order(db, order_data, user["uid"])
        return order
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to place order")

@router.get("/", response_model=List[OrderOut])
def get_my_orders(
    db: Session = Depends(get_db),
    user=Depends(verify_firebase_token)
):
    try:
        orders = get_orders_by_user(db, user["uid"])
        return orders
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to fetch orders")

@router.get("/{order_id}", response_model=OrderOut)
def get_order_details(
    order_id: str,
    db: Session = Depends(get_db),
    user=Depends(verify_firebase_token)
):
    try:
        order = get_order_by_id(db, order_id, user["uid"])
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        return order
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to fetch order details")
