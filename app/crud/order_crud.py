from sqlalchemy.orm import Session
from app.models.order_model import Order
from app.models.order_item_model import OrderItem
from app.models.payment_model import Payment
from app.schemas.order_schema import OrderCreate
import uuid

def create_order(db: Session, order_data: OrderCreate, user_uid: str) -> Order:
    #  Prevent duplicate order for same payment_id
    existing_order = db.query(Order).filter_by(payment_id=order_data.payment_id).first()
    if existing_order:
        raise ValueError("An order with this payment ID already exists.")

    #  Ensure payment exists and is successful
    payment = db.query(Payment).filter(
        Payment.payment_intent_id == order_data.payment_id,
        Payment.status == "succeeded"
    ).first()

    if not payment:
        raise ValueError("Invalid or incomplete payment.")

    # Create new order
    order = Order(
        id=str(uuid.uuid4()),
        user_uid=user_uid,
        total_amount=order_data.total_amount,
        payment_id=order_data.payment_id,
        status="confirmed"
    )
    db.add(order)
    db.flush()  # Flush to assign order.id before adding items

    #  Add order items
    for item in order_data.items:
        db.add(OrderItem(
            order_id=order.id,
            product_name=item.product_name,
            quantity=item.quantity,
            unit_price=item.unit_price
        ))

    db.commit()
    db.refresh(order)
    return order
