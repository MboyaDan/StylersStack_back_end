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
    logger.info(f"FCM update request: uid={user['uid']}, token={data.fcm_token}")

    db_user: User = db.query(User).filter(User.uid == user["uid"]).first()
    if not db_user:
        logger.warning(f"User not found: {user['uid']}")
        raise HTTPException(status_code=404, detail="User not found")

    logger.info(f"DB user found: {db_user.uid}, current token: {db_user.fcm_token}")

    if not data.fcm_token or len(data.fcm_token) < 10:
        logger.warning(f"Invalid FCM token from user {user['uid']}: {data.fcm_token}")
        raise HTTPException(status_code=400, detail="Invalid FCM token")

    if db_user.fcm_token == data.fcm_token:
        logger.info(f"No update needed, token already up-to-date for user {user['uid']}")
        return {"message": "FCM token already up-to-date"} 

    db_user.fcm_token = data.fcm_token
    db.commit()
    db.refresh(db_user)

    logger.info(f"FCM token updated for user {user['uid']} to: {db_user.fcm_token}")
    return {"message": "FCM token updated successfully"}
