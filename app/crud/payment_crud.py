from sqlalchemy.orm import Session
from app.models.payment_model import Payment
from app.schemas.payment_schema import PaymentCreate
import uuid
from datetime import datetime

def create_payment(db: Session, payment_data: PaymentCreate, user_id: str) -> Payment:
    payment_intent_id = str(uuid.uuid4())
    status = "succeeded" if payment_data.payment_method.lower() == "cod" else "pending"

    payment = Payment(
        id=str(uuid.uuid4()),
        order_id=payment_data.order_id,
        user_id=user_id,
        amount=payment_data.amount,
        currency=payment_data.currency,
        payment_method=payment_data.payment_method.lower(),
        payment_intent_id=payment_intent_id,
        status=status,
        created_at=datetime.utcnow()
    )

    db.add(payment)
    db.commit()
    db.refresh(payment)
    return payment

def get_payment_by_order_id(db: Session, order_id: str) -> Payment | None:
    return db.query(Payment).filter(Payment.order_id == order_id).first()

def get_payment_by_intent_id(db: Session, intent_id: str) -> Payment | None:
    return db.query(Payment).filter(Payment.payment_intent_id == intent_id).first()

def update_payment_status(db: Session, payment_intent_id: str, status: str) -> Payment | None:
    payment = get_payment_by_intent_id(db, payment_intent_id)
    if payment:
        payment.status = status
        db.commit()
        db.refresh(payment)
        return payment
    return None

def process_refund(db: Session, payment_intent_id: str, amount: float) -> bool:
    payment = get_payment_by_intent_id(db, payment_intent_id)
    if payment and amount <= payment.amount:
        payment.status = "refunded"
        db.commit()
        return True
    return False
