import logging
from fastapi import Request
from sqlalchemy.orm import Session
from app.crud import payment_crud
from app.models.payment_model import Payment
from app.models.user_model import User
from app.services.notification_service import send_fcm_notification


def initiate_payment(db: Session, payment_data, user_id: str):
    if payment_data.payment_method.lower() == "cod":
        return payment_crud.create_payment(db, payment_data, user_id, status="pending")
    return payment_crud.create_payment(db, payment_data, user_id)


def confirm_payment(db: Session, payment_intent_id: str) -> bool:
    payment = payment_crud.update_payment_status(db, payment_intent_id, "succeeded")
    return payment is not None


def get_payment_status(db: Session, order_id: str):
    return payment_crud.get_payment_by_order_id(db, order_id)


def process_refund(db: Session, payment_intent_id: str, amount: float) -> bool:
    return payment_crud.process_refund(db, payment_intent_id, amount)


async def handle_mpesa_callback(request: Request, db: Session, background_tasks):
    data = await request.json()
    logging.info(f"M-Pesa callback data: {data}")

    body = data.get("Body", {}).get("stkCallback", {})
    result_code = body.get("ResultCode")
    callback_metadata = body.get("CallbackMetadata", {}).get("Item", [])

    order_id = None
    for item in callback_metadata:
        if item.get("Name") == "AccountReference":
            order_id = item.get("Value")
            break

    if not order_id:
        logging.error("Order ID missing in M-Pesa callback")
        return {"ResultCode": 1, "ResultDesc": "Order ID missing"}

    payment: Payment = payment_crud.get_payment_by_order_id(db, order_id)
    if not payment:
        logging.error(f"Payment record not found for order_id: {order_id}")
        return {"ResultCode": 1, "ResultDesc": "Payment record not found"}

    # Idempotency: check if payment is already processed
    if payment.status in ("succeeded", "failed"):
        logging.info(f"Payment already processed with status: {payment.status}")
        return {"ResultCode": 0, "ResultDesc": "Callback already processed"}

    # Update payment status
    new_status = "succeeded" if result_code == 0 else "failed"
    payment_crud.update_payment_status(db, order_id, new_status)

    user: User = payment.user
    if user and user.fcm_token:
        title = "Payment Status Update"
        body = f"Your payment for order {order_id} has been {'successful' if new_status == 'succeeded' else 'failed'}."
        data = {"order_id": order_id, "status": new_status}
        
        # Send push notification
        background_tasks.add_task(
            send_fcm_notification,
            token=user.fcm_token,
            title=title,
            body=body,
            data=data
        )
    logging.info(f"Payment status updated to {new_status} for order_id: {order_id}")
    # Return success response
    logging.info("M-Pesa callback processed successfully")
        
    return {"ResultCode": 0, "ResultDesc": "Callback received successfully"}
