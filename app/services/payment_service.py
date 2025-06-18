import logging
from fastapi import Request, BackgroundTasks
from sqlalchemy.orm import Session
from app.crud import payment_crud
from app.models.payment_model import Payment
from app.models.user_model import User
from app.services.notification_service import send_fcm_notification
from app.services.mpesa_services import query_mpesa_payment_status, initiate_mpesa_payment
import re
from app.schemas.payment_schema import PaymentCreate
from app.schemas.payment_schema import PaymentMethod

def initiate_payment(db: Session, payment_data: PaymentCreate, user_id: str):
    # Step 1: Create payment in DB
    payment = payment_crud.create_payment(db, payment_data, user_id)

    # Step 2: If payment method is mpesa, trigger STK push
    if payment_data.payment_method == PaymentMethod.mpesa:
        try:
            logging.info(f"[M-Pesa] Initiating payment for OrderID: {payment.order_id}")
            logging.info(f"[M-Pesa] Amount: {payment.amount}, Phone: {payment.phone_number}")
            logging.debug(f"[M-Pesa] Full Payment Data: {payment_data}")

            # STK Push
            response = initiate_mpesa_payment(payment)
            logging.info(f"[M-Pesa] STK Response: {response}")

            if "error" in response:
                logging.error(f"[M-Pesa] STK Push failed: {response.get('details') or response.get('error')}")
            else:
                checkout_id = response.get("CheckoutRequestID")
                if checkout_id:
                    logging.info(f"[M-Pesa] CheckoutRequestID received: {checkout_id}")
                    payment_crud.update_checkout_id(db, payment.payment_intent_id, checkout_id)

        except Exception:
            logging.exception("[M-Pesa] Unexpected exception during STK Push")

    return payment




def confirm_payment(db: Session, payment_intent_id: str) -> bool:
    """
    Force-mark a payment as succeeded (e.g., for COD after delivery confirmation).
    """
    payment = payment_crud.update_payment_status(db, payment_intent_id, "succeeded")
    return payment is not None


def get_payment_status(db: Session, order_id: str) -> Payment | None:
    """
    Fetch the current payment status and optionally query M-Pesa if still pending.
    """
    payment = payment_crud.get_payment_by_order_id(db, order_id)
    if not payment:
        logging.error(f"Payment not found for order_id: {order_id}")
        return None

    if payment.status in ("succeeded", "failed", "cancelled"):
        return payment

    if payment.payment_method == "mpesa":
        response = query_mpesa_payment_status(payment.payment_intent_id)
        if "error" in response:
            logging.error(f"M-Pesa status query failed: {response['error']}")
            return payment

        result_code = response.get("ResultCode")
        if result_code == 0:
            new_status = "succeeded"
        elif result_code == 1032:
            new_status = "cancelled"
        else:
            new_status = "failed"

        if new_status != payment.status:
            payment_crud.update_payment_status(db, payment.payment_intent_id, new_status)
            db.refresh(payment)

    return payment


def process_refund(db: Session, payment_intent_id: str, amount: float) -> bool:
    return payment_crud.process_refund(db, payment_intent_id, amount)


async def handle_mpesa_callback(request: Request, db: Session, background_tasks: BackgroundTasks):
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

    payment: Payment = payment_crud.get_payment_by_order_id(db, order_id)
    if not payment:
        logging.error(f"Payment not found for order_id: {order_id}")
        return {"ResultCode": 1, "ResultDesc": "Payment not found"}

    if payment.status in ("succeeded", "failed"):
        logging.info(f"Payment already processed with status: {payment.status}")
        return {"ResultCode": 0, "ResultDesc": "Callback already processed"}

    new_status = "succeeded" if result_code == 0 else "failed"
    updated = payment_crud.update_payment_status(db, payment.payment_intent_id, new_status)

    if not updated:
        logging.error(f"Failed to update payment status for order_id: {order_id}")
        return {"ResultCode": 1, "ResultDesc": "Update failed"}

    # Send notification
    user: User = payment.user
    if user and user.fcm_token:
        title = "Payment Status Update"
        body = f"Your payment for order {order_id} was {'successful' if new_status == 'succeeded' else 'unsuccessful'}."
        data = {"order_id": order_id, "status": new_status}
        background_tasks.add_task(send_fcm_notification, token=user.fcm_token, title=title, body=body, data=data)

    logging.info(f"Payment status updated to {new_status} for order_id: {order_id}")
    return {"ResultCode": 0, "ResultDesc": "Callback received successfully"}
