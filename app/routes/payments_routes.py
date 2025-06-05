from fastapi import APIRouter, Depends, HTTPException, Request, BackgroundTasks
from sqlalchemy.orm import Session

from app.schemas.payment_schema import (
    PaymentCreate, PaymentResponse, PaymentConfirm, RefundRequest
)
from app.dependencies import get_db
from app.utils.firebase_auth import verify_firebase_token
from app.services import payment_service

router = APIRouter(prefix="/payment", tags=["Payments"])


@router.post("/initiate", response_model=PaymentResponse)
def initiate_payment(
    payment: PaymentCreate,
    db: Session = Depends(get_db),
    user=Depends(verify_firebase_token)
):
    return payment_service.initiate_payment(db, payment, user["uid"])


@router.post("/confirm")
def confirm_payment(
    data: PaymentConfirm,
    db: Session = Depends(get_db),
    user=Depends(verify_firebase_token)
):
    updated = payment_service.confirm_payment(db, data.payment_intent_id)
    if not updated:
        raise HTTPException(status_code=404, detail="Payment not found")
    return {"message": "Payment confirmed successfully"}


@router.get("/status/{order_id}", response_model=PaymentResponse)
def fetch_payment_status(
    order_id: str,
    db: Session = Depends(get_db),
    user=Depends(verify_firebase_token)
):
    payment = payment_service.get_payment_status(db, order_id)
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    return payment


@router.post("/refund")
def refund_payment(
    data: RefundRequest,
    db: Session = Depends(get_db),
    user=Depends(verify_firebase_token)
):
    success = payment_service.process_refund(db, data.payment_intent_id, data.amount)
    if not success:
        raise HTTPException(status_code=400, detail="Refund failed")
    return {"message": "Refund processed successfully"}


@router.post("/mpesa/callback")
async def mpesa_callback(
    request: Request,
    db: Session = Depends(get_db),
    background_tasks: BackgroundTasks = None
):
    return await payment_service.handle_mpesa_callback(request, db, background_tasks)
