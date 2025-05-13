#Where SessionLocal is defined
from .database import SessionLocal
from sqlalchemy.orm import Session
from fastapi import Depends


def get_db():
    db = SessionLocal()#create a new session using SessionLocal
    try:
        yield db #Yield the session for use in route functions
    finally:
        db.close() #Ensure the session is closed after use
