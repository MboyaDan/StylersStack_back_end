from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.schemas.favorite_schema import FavoriteCreate, FavoriteOut
from app.crud.favorite_crud import create_favorite, get_favorites_for_user,delete_favorite_by_product_and_user
from app.dependencies import get_db
from app.utils.firebase_auth import verify_firebase_token

router = APIRouter(prefix="/favorites", tags=["Favorites"])

@router.post("/", response_model=FavoriteOut)
def add_favorite(
    favorite: FavoriteCreate,
    db: Session = Depends(get_db),
    user=Depends(verify_firebase_token),
):
    return create_favorite(db, favorite)

@router.get("/", response_model=List[FavoriteOut])
def get_favorites(
    db: Session = Depends(get_db),
    user=Depends(verify_firebase_token),
):
    return get_favorites_for_user(db, user["uid"])


@router.delete("/{product_id}")
def delete_favorite(
    product_id: int,
    db: Session = Depends(get_db),
    user=Depends(verify_firebase_token),
):
    return delete_favorite_by_product_and_user(db, product_id, user["uid"])

