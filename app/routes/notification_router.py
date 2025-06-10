from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.utils.firebase_auth import verify_firebase_token
from app.schemas.user_schema import FCMTokenUpdate
from app.models.user_model import User

router = APIRouter(prefix="/user", tags=["Users"])

@router.patch("/fcm-token")
def update_fcm_token(
    data: FCMTokenUpdate,
    db: Session = Depends(get_db),
    user=Depends(verify_firebase_token)
):
    db_user: User = db.query(User).filter(User.uid == user["uid"]).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if db_user.fcm_token == data.fcm_token:
        raise HTTPException(status_code=400, detail="FCM token is already set to this value")

    db_user.fcm_token = data.fcm_token
    db.commit()
    db.refresh(db_user)

    return {"message": "FCM token updated successfully"}
