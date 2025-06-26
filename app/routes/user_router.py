from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import logging

from app.dependencies import get_db
from app.utils.firebase_auth import verify_firebase_token
from app.schemas.user_schema import FCMTokenUpdate
from app.models.user_model import User

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/user", tags=["Users"])

@router.patch("/fcm-token")
def update_fcm_token(
    data: FCMTokenUpdate,
    db: Session = Depends(get_db),
    user=Depends(verify_firebase_token)
):
    uid = user["uid"]
    email = user.get("email")

    logger.info(f"FCM update request: uid={uid}, token={data.fcm_token}")

    db_user: User = db.query(User).filter(User.uid == uid).first()

    if not db_user:
        logger.warning(f"User not found in DB: {uid}, creating new user")

        # Only uid and email used to match Flutter's UserModel
        db_user = User(
            uid=uid,
            email=email,
            fcm_token=data.fcm_token
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)

        logger.info(f"New user created and FCM token stored: {db_user.uid}")
        return {"message": "User created and FCM token saved"}

    # Validate the incoming token
    if not data.fcm_token or len(data.fcm_token) < 10:
        logger.warning(f"Invalid FCM token from user {uid}: {data.fcm_token}")
        raise HTTPException(status_code=400, detail="Invalid FCM token")

    # Check if the token is already the same
    if db_user.fcm_token == data.fcm_token:
        logger.info(f"No update needed, token already up-to-date for user {uid}")
        return {"message": "FCM token already up-to-date"} 

    # Update the token
    db_user.fcm_token = data.fcm_token
    db.commit()
    db.refresh(db_user)

    logger.info(f"FCM token updated for user {uid} to: {db_user.fcm_token}")
    return {"message": "FCM token updated successfully"}
