from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.order_schema import OrderCreate, OrderOut
from app.crud.order_crud import create_order
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
        # Inject user UID from Firebase into the order data
        return create_order(db, order_data, user["uid"])
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
