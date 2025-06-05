import logging
from fastapi import Request
from sqlalchemy.orm import Session
from app.crud import payment_crud
from app.models.payment_model import Payment
from app.models.user_model import User
from app.services.notification_service import send_fcm_notification
from app.services.mpesa_services import query_mpesa_payment_status

def initiate_payment(db: Session, payment_data, user_id: str):
    # If COD (Cash on Delivery), mark as pending
    status = "pending" if payment_data.payment_method.lower() == "cod" else "pending"  # Keep as "pending" for all methods, let confirmation handle success
    return payment_crud.create_payment(db, payment_data, user_id)


def confirm_payment(db: Session, payment_intent_id: str) -> bool:
    payment = payment_crud.update_payment_status(db, payment_intent_id, "succeeded")
    return payment is not None


def get_payment_status(db: Session, order_id: str):
    payment = payment_crud.get_payment_by_order_id(db, order_id)
    if not payment:
        logging.error(f"Payment not found for order_id: {order_id}")
        return None

    # If already finalized, no need to re-query
    if payment.status in ("succeeded", "failed", "cancelled"):
        return payment

    # Query M-Pesa only for M-Pesa payments that are still pending
    if payment.payment_method.lower() == "mpesa":
        response = query_mpesa_payment_status(payment.payment_intent_id)
        if "error" in response:
            logging.error(f"M-Pesa status query failed: {response['error']}")
            return payment  # Return the current known state

        # Handle more granular status
        result_code = response.get("ResultCode")
        if result_code == 0:
            new_status = "succeeded"
        elif result_code == 1032:
            new_status = "cancelled"
        else:
            new_status = "failed"

        # Only update if status actually changed
        if new_status != payment.status:
            payment_crud.update_payment_status(db, payment.payment_intent_id, new_status)
            db.refresh(payment)  # Keep object in sync

    return payment




def process_refund(db: Session, payment_intent_id: str, amount: float) -> bool:
    return payment_crud.process_refund(db, payment_intent_id, amount)


async def handle_mpesa_callback(request: Request, db: Session, background_tasks):
    data = await request.json()
    logging.info(f"M-Pesa callback data: {data}")

    stk_callback = data.get("Body", {}).get("stkCallback", {})
    result_code = stk_callback.get("ResultCode")
    callback_metadata = stk_callback.get("CallbackMetadata", {}).get("Item", [])

    order_id = None
    for item in callback_metadata:
        if item.get("Name") == "AccountReference":
            order_id = str(item.get("Value"))
            break

    if not order_id:
        logging.error("Order ID missing in M-Pesa callback")
        return {"ResultCode": 1, "ResultDesc": "Order ID missing"}

    # Fetch payment using order_id
    payment: Payment = payment_crud.get_payment_by_order_id(db, order_id)
    if not payment:
        logging.error(f"Payment not found for order_id: {order_id}")
        return {"ResultCode": 1, "ResultDesc": "Payment not found"}

    # Idempotency: if already processed
    if payment.status in ("succeeded", "failed"):
        logging.info(f"Payment already processed with status: {payment.status}")
        return {"ResultCode": 0, "ResultDesc": "Callback already processed"}

    # Update status based on result code
    new_status = "succeeded" if result_code == 0 else "failed"
    updated = payment_crud.update_payment_status(db, payment.payment_intent_id, new_status)

    if not updated:
        logging.error(f"Failed to update payment status for order_id: {order_id}")
        return {"ResultCode": 1, "ResultDesc": "Update failed"}

    # Send push notification to user
    user: User = payment.user
    if user and user.fcm_token:
        title = "Payment Status Update"
        body = f"Your payment for order {order_id} was {'successful' if new_status == 'succeeded' else 'unsuccessful'}."
        data = {"order_id": order_id, "status": new_status}

        background_tasks.add_task(
            send_fcm_notification,
            token=user.fcm_token,
            title=title,
            body=body,
            data=data
        )

    logging.info(f"Payment status updated to {new_status} for order_id: {order_id}")
    return {"ResultCode": 0, "ResultDesc": "Callback received successfully"}
