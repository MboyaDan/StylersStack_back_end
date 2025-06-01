from pydantic import BaseModel, EmailStr, ConfigDict
from datetime import datetime

class UserBase(BaseModel):
    uid: str
    email: EmailStr

class UserCreate(UserBase):
    pass

class UserInDB(UserBase):
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
