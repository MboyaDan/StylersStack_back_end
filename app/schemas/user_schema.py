from pydantic import BaseModel, EmailStr, ConfigDict
from datetime import datetime

class UserBase(BaseModel):
    uid: str
    email: EmailStr
    fcm_token: str | None = None  # Firebase Cloud Messaging token

class UserCreate(UserBase):
    pass

class UserInDB(UserBase):
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
class FCMTokenUpdate(BaseModel):
    fcm_token: str

    model_config = ConfigDict(from_attributes=True)