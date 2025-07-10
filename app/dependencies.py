#Where SessionLocal is defined
from .database import SessionLocal
from sqlalchemy.orm import Session
from fastapi import Depends

from fastapi import Request, HTTPException, status
from fastapi.responses import RedirectResponse

def get_db():
    db = SessionLocal()#create a new session using SessionLocal
    try:
        yield db #Yield the session for use in route functions
    finally:
        db.close() #Ensure the session is closed after use


# 🔐 Protect admin routes



def require_admin(request: Request):
    user = request.session.get("user")
    if not user:
        raise HTTPException(status_code=403, detail="Not authenticated")
    return user
