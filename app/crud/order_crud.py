from sqlalchemy.orm import Session, joinedload
from app.models.order_model import Order
from app.models.order_item_model import OrderItem
from app.models.payment_model import Payment
from app.schemas.order_schema import OrderCreate
import time


def create_order(db: Session, order_data: OrderCreate, user_uid: str) -> Order:
    #Prevent duplicate order for same payment_id
    if db.query(Order).filter_by(payment_id=order_data.payment_id).first():
        raise ValueError("An order with this payment ID already exists.")

    # Ensure payment exists and is successful
    payment = (
        db.query(Payment)
        .filter(
            Payment.payment_intent_id == order_data.payment_id,
            Payment.status == "succeeded"
        )
        .first()
    )
    if not payment:
        raise ValueError("Invalid or incomplete payment.")

    if not order_data.items or len(order_data.items) == 0:
        raise ValueError("No order items provided.")

    #Create order
    order = Order(
        id=f"ORD-{int(time.time() * 1000)}",
        user_uid=user_uid,
        total_amount=order_data.total_amount,
        payment_id=order_data.payment_id,
        status="confirmed"
    )

    #  Attach items via relationship instead of manual insert
    order.items = [
        OrderItem(
            product_name=item.product_name,
            quantity=item.quantity,
            unit_price=item.unit_price
        )
        for item in order_data.items
    ]

    db.add(order)
    db.commit()
    db.refresh(order)  # ensures fresh object with items loaded

    return order


def get_orders_by_user(db: Session, user_uid: str):
    return (
        db.query(Order)
        .options(joinedload(Order.items))
        .filter(Order.user_uid == user_uid)
        .order_by(Order.created_at.desc())
        .all()
    )

def get_order_by_id(db: Session, order_id: str, user_uid: str):
    return (
        db.query(Order)
        .options(joinedload(Order.items)) 
        .filter(Order.id == order_id, Order.user_uid == user_uid)
        .first()
    )

