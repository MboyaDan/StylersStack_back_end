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
            logging.info(f"[M-Pesa] Initiating payment for PaymentIntentID: {payment.payment_intent_id}")
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
                    db.commit()

        except Exception:
            logging.exception("[M-Pesa] Unexpected exception during STK Push")

    return payment


def confirm_payment(db: Session, payment_intent_id: str) -> bool:
    return payment_crud.update_payment_status(db, payment_intent_id, "succeeded") is not None


def get_payment_status(db: Session, payment_intent_id: str) -> Payment | None:
    payment = payment_crud.get_payment_by_intent_id(db, payment_intent_id)
    if not payment:
        logging.error(f"Payment not found for payment_intent_id: {payment_intent_id}")
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
    if not stk_callback:
        logging.error("[M-Pesa] Missing 'stkCallback' in payload.")
        return {"ResultCode": 1, "ResultDesc": "Invalid callback payload"}

    result_code = stk_callback.get("ResultCode")
    checkout_id = stk_callback.get("CheckoutRequestID")
    callback_metadata = stk_callback.get("CallbackMetadata", {}).get("Item", [])

    if not checkout_id:
        logging.error("[M-Pesa] Missing CheckoutRequestID in callback.")
        return {"ResultCode": 1, "ResultDesc": "Missing CheckoutRequestID"}

    # Retry logic
    payment = None
    for attempt in range(3):
        payment = payment_crud.get_payment_by_checkout_id(db, checkout_id)
        if payment:
            break
        logging.warning(f"[M-Pesa] Payment not yet found for CheckoutRequestID: {checkout_id}, attempt {attempt + 1}")
        time.sleep(0.5)

    if not payment:
        logging.error(f"[M-Pesa] No matching payment for CheckoutRequestID: {checkout_id}")
        return {"ResultCode": 1, "ResultDesc": "Payment not found"}

    if payment.status in ("succeeded", "failed"):
        logging.info(f"[M-Pesa] Payment already marked as {payment.status}")
        return {"ResultCode": 0, "ResultDesc": "Already processed"}

    new_status = "succeeded" if result_code == 0 else "failed"
    logging.info(f"[M-Pesa] Updating status to '{new_status}' for payment_intent_id: {payment.payment_intent_id}")

    updated = payment_crud.update_payment_status(db, payment.payment_intent_id, new_status)
    if not updated:
        logging.error(f"[M-Pesa] DB update failed for payment_intent_id: {payment.payment_intent_id}")
        return {"ResultCode": 1, "ResultDesc": "Update failed"}

    db.commit()

    # Notify user
    user: User = payment.user
    if user and user.fcm_token:
        title = "Payment Status Update"
        body = f"Your payment for order {payment.payment_intent_id} KES was {'successful' if new_status == 'succeeded' else 'unsuccessful'}."
        background_tasks.add_task(
            send_fcm_notification,
            token=user.fcm_token,
            title=title,
            body=body,
            data={"payment_intent_id": payment.payment_intent_id, "status": new_status,"total_amount": str(payment.amount)}
        )

    return {"ResultCode": 0, "ResultDesc": "Callback received successfully"}
