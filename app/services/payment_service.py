import logging
import json
import time
from fastapi import Request, BackgroundTasks
from sqlalchemy.orm import Session
from app.crud import payment_crud
from app.models.payment_model import Payment
from app.models.user_model import User
from app.services.notification_service import send_fcm_notification
from app.services.mpesa_services import query_mpesa_payment_status, initiate_mpesa_payment
from app.schemas.payment_schema import PaymentCreate, PaymentMethod


def initiate_payment(db: Session, payment_data: PaymentCreate, user_id: str):
    payment = payment_crud.create_payment(db, payment_data, user_id)

    if payment_data.payment_method == PaymentMethod.mpesa:
        try:
            logging.info(f"[M-Pesa] Initiating payment for OrderID: {payment.order_id}")
            logging.info(f"[M-Pesa] Amount: {payment.amount}, Phone: {payment.phone_number}")
            logging.debug(f"[M-Pesa] Full Payment Data: {payment_data}")

            response = initiate_mpesa_payment(payment)
            logging.info(f"[M-Pesa] STK Response: {response}")

            if "error" in response:
                logging.error(f"[M-Pesa] STK Push failed: {response.get('details') or response.get('error')}")
            else:
                checkout_id = response.get("CheckoutRequestID")
                if checkout_id:
                    logging.info(f"[M-Pesa] CheckoutRequestID received: {checkout_id}")
                    payment_crud.update_checkout_id(db, payment.payment_intent_id, checkout_id)
                    db.commit()  #  Ensure it's written before callback arrives

        except Exception:
            logging.exception("[M-Pesa] Unexpected exception during STK Push")

    return payment


def confirm_payment(db: Session, payment_intent_id: str) -> bool:
    return payment_crud.update_payment_status(db, payment_intent_id, "succeeded") is not None


def get_payment_status(db: Session, order_id: str) -> Payment | None:
    payment = payment_crud.get_payment_by_order_id(db, order_id)
    if not payment:
        logging.error(f"Payment not found for order_id: {order_id}")
        return None

    if payment.status in ("succeeded", "failed", "cancelled"):
        return payment

    if payment.payment_method == "mpesa":
        response = query_mpesa_payment_status(payment.payment_intent_id)
        if "error" in response:
            logging.error(f"[M-Pesa] Status query failed: {response['error']}")
            return payment

        result_code = response.get("ResultCode")
        new_status = (
            "succeeded" if result_code == 0 else
            "cancelled" if result_code == 1032 else
            "failed"
        )

        if new_status != payment.status:
            payment_crud.update_payment_status(db, payment.payment_intent_id, new_status)
            db.refresh(payment)

    return payment


def process_refund(db: Session, payment_intent_id: str, amount: float) -> bool:
    return payment_crud.process_refund(db, payment_intent_id, amount)


async def handle_mpesa_callback(request: Request, db: Session, background_tasks: BackgroundTasks):
    data = await request.json()
    logging.info("[M-Pesa Callback] Raw payload:\n" + json.dumps(data, indent=2))

    stk_callback = data.get("Body", {}).get("stkCallback", {})
    result_code = stk_callback.get("ResultCode")
    callback_metadata = stk_callback.get("CallbackMetadata", {}).get("Item", [])

    order_id = None
    payment = None

    # Try to extract AccountReference
    for item in callback_metadata:
        if item.get("Name") == "AccountReference":
            order_id = str(item.get("Value"))
            logging.info(f"[M-Pesa] Extracted order_id from AccountReference: {order_id}")
            break

    # Fallback: use CheckoutRequestID
    if not order_id:
        checkout_id = stk_callback.get("CheckoutRequestID")
        if checkout_id:
            logging.warning(f"[M-Pesa] AccountReference missing, using CheckoutRequestID: {checkout_id}")
            # 🧠Retry logic in case payment not written yet
            for attempt in range(3):
                payment = payment_crud.get_payment_by_checkout_id(db, checkout_id)
                if payment:
                    order_id = payment.order_id
                    break
                time.sleep(0.5)  # wait a bit before retry
        else:
            logging.error("[M-Pesa] Missing AccountReference and CheckoutRequestID")
            return {"ResultCode": 1, "ResultDesc": "Missing order identifiers"}

    # Fallback: fetch by order_id
    if not payment:
        payment = payment_crud.get_payment_by_order_id(db, order_id)

    if not payment:
        logging.error(f"[M-Pesa] Payment not found for order_id: {order_id}")
        return {"ResultCode": 1, "ResultDesc": "Payment not found"}

    if payment.status in ("succeeded", "failed"):
        logging.info(f"[M-Pesa] Payment already marked as {payment.status}")
        return {"ResultCode": 0, "ResultDesc": "Already processed"}

    # Finalize and update status
    new_status = "succeeded" if result_code == 0 else "failed"
    logging.info(f"[M-Pesa] Updating status to '{new_status}' for order_id: {order_id}")

    updated = payment_crud.update_payment_status(db, payment.payment_intent_id, new_status)
    if not updated:
        logging.error(f"[M-Pesa] DB update failed for payment_intent_id: {payment.payment_intent_id}")
        return {"ResultCode": 1, "ResultDesc": "Update failed"}

    db.commit()  # Ensure the update is persisted

    # notify user via fcm
    user: User = payment.user
    if user and user.fcm_token:
        title = "Payment Status Update"
        body = f"Your payment for order {order_id} was {'successful' if new_status == 'succeeded' else 'unsuccessful'}."
        background_tasks.add_task(send_fcm_notification, token=user.fcm_token, title=title, body=body, data={"order_id": order_id, "status": new_status})

    return {"ResultCode": 0, "ResultDesc": "Callback received successfully"}
