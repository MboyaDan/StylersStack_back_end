from sqlalchemy.orm import Session
from app.models.payment_model import Payment
from app.schemas.payment_schema import PaymentCreate
from datetime import datetime, timezone
import time
import random
import string

def generate_unique_payment_intent_id(db: Session, prefix="ORD") -> str:
    """
    Generates a unique payment intent ID with a timestamp and random string,
    and checks DB for uniqueness to avoid rare collisions.
    """
    while True:
        timestamp = int(time.time() * 1000)
        random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
        intent_id = f"{prefix}-{timestamp}-{random_part}"
        
        exists = db.query(Payment).filter_by(payment_intent_id=intent_id).first()
        if not exists:
            return intent_id



def create_payment(db: Session, payment_data: PaymentCreate, user_id: str) -> Payment:
    payment_intent_id = generate_unique_payment_intent_id(db)
    status = "succeeded" if payment_data.payment_method.lower() == "cod" else "pending"

    payment = Payment(
        payment_intent_id=payment_intent_id,
        user_id=user_id,
        amount=payment_data.amount,
        currency=payment_data.currency,
        payment_method=payment_data.payment_method.lower(),
        status=status,
        phone_number=payment_data.phone_number,
        checkout_request_id=payment_data.checkout_request_id,
    )
    print(f"[create_payment] Received method={payment_data.payment_method}, phone={payment_data.phone_number}")


    db.add(payment)
    db.commit()
    db.refresh(payment)
    return payment

def get_payment_by_intent_id(db: Session, intent_id: str) -> Payment | None:
    return db.query(Payment).filter(Payment.payment_intent_id == intent_id).first()

def update_payment_status(db: Session, payment_intent_id: str, status: str) -> bool:
    payment = get_payment_by_intent_id(db, payment_intent_id)
    if payment:
        payment.status = status
        db.commit()
        return True
    return False

def process_refund(db: Session, payment_intent_id: str, amount: float) -> bool:
    payment = get_payment_by_intent_id(db, payment_intent_id)
    if payment and amount <= payment.amount:
        payment.status = "refunded"
        db.commit()
        return True
    return False

def update_checkout_id(db: Session, payment_intent_id: str, checkout_request_id: str) -> Payment | None:
    payment = get_payment_by_intent_id(db, payment_intent_id)
    if payment:
        payment.checkout_request_id = checkout_request_id
        db.commit()
        db.refresh(payment)
        return payment
    return None
def get_payment_by_checkout_id(db: Session, checkout_id: str) -> Payment | None:
    return db.query(Payment).filter(Payment.checkout_request_id == checkout_id).first()




