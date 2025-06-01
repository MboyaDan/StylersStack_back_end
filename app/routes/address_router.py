from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import logging

from app.schemas.address_schema import Address, AddressCreate
from app.schemas.user_schema import UserCreate
from app.crud.address_crud import upsert_address, get_address, delete_address
from app.dependencies import get_db
from app.utils.firebase_auth import verify_firebase_token

router = APIRouter(prefix="/address", tags=["Address"])
logger = logging.getLogger(__name__)

# ──────────────── CREATE / UPDATE ────────────────
@router.post("/", response_model=Address, status_code=status.HTTP_201_CREATED)
def create_or_update(
    addr_in: AddressCreate,
    db: Session = Depends(get_db),
    user = Depends(verify_firebase_token),
):
    user_data = UserCreate(uid=user["uid"], email=user["email"])
    return upsert_address(db, user_data, addr_in)


# ──────────────── READ ────────────────
@router.get("/", response_model=Address)
def read(
    db: Session = Depends(get_db),
    user = Depends(verify_firebase_token),
):
    logger.info(f"Fetching address for UID: {user['uid']}")
    db_addr = get_address(db, user["uid"])
    if not db_addr:
        logger.warning(f"No address found for UID: {user['uid']}")
        raise HTTPException(status_code=404, detail="Address not found")
    return db_addr


# ──────────────── DELETE ────────────────
@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
def delete(
    db: Session = Depends(get_db),
    user = Depends(verify_firebase_token),
):
    deleted = delete_address(db, user["uid"])
    if not deleted:
        raise HTTPException(status_code=404, detail="Address not found")
    return {"detail": "Address deleted successfully"}
