from sqlalchemy.orm import Session
from typing import Optional

from app.models.address_model import Address
from app.models.user_model import User
from app.schemas.address_schema import AddressCreate
from app.schemas.user_schema import UserCreate


def upsert_address(
    db: Session,
    user_data: UserCreate,  # expects uid and email
    addr_in: AddressCreate
) -> Address:
    # Step 1: Check if user exists
    user = db.query(User).filter(User.uid == user_data.uid).first()
    if not user:
        # Create user using data from Firebase
        user = User(uid=user_data.uid, email=user_data.email)
        db.add(user)
        db.commit()
        db.refresh(user)

    # Step 2: Upsert address
    db_addr = db.query(Address).filter(Address.user_uid == user_data.uid).first()
    if db_addr:
        db_addr.address = addr_in.address
    else:
        db_addr = Address(user_uid=user_data.uid, **addr_in.dict())
        db.add(db_addr)

    db.commit()
    db.refresh(db_addr)
    return db_addr


# ────────────────────────────── READ ──────────────────────────────
def get_address(db: Session, user_uid: str) -> Optional[Address]:
    return db.query(Address).filter(Address.user_uid == user_uid).first()


# ────────────────────────────── DELETE ──────────────────────────────
def delete_address(db: Session, user_uid: str) -> bool:
    db_addr = get_address(db, user_uid)
    if not db_addr:
        return False
    db.delete(db_addr)
    db.commit()
    return True
