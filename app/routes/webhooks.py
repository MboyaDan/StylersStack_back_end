from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app.dependencies import get_db
from app.schemas.payment import MpesaWebhookPayload
from app.crud.payment_crud import update_payment_status
from app.utils.notifications import send_push_notification

router = APIRouter(prefix="/webhook", tags=["Webhooks"])

@router.post("/mpesa")
def mpesa_webhook(request: Request, db: Session = Depends(get_db)):
    payload = request.json()
    try:
        webhook_data = MpesaWebhookPayload.parse_obj(payload)
        stk_callback = webhook_data.Body.get("stkCallback")
        if not stk_callback:
            raise HTTPException(status_code=400, detail="Missing stkCallback")

        merchant_request_id = stk_callback.get("MerchantRequestID")
        result_code = stk_callback.get("ResultCode", 1)
        result_desc = stk_callback.get("ResultDesc", "Unknown")

        update_payment_status(db, merchant_request_id, stk_callback)

        send_push_notification(
            token="some_token",
            title="Payment Status",
            body=f"Payment {'Successful' if result_code == 0 else 'Failed'}",
            data={"order_id": merchant_request_id}
        )

        return JSONResponse({"message": "Processed"}, status_code=200)

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
