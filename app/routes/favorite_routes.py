# app/routes/favorite_routes.py
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List

from app.schemas.favorite_schema import FavoriteCreate, FavoriteOut
from app.crud.favorite_crud import (
    create_favorite,
    get_favorites_for_user,
    delete_favorite_by_product_and_user,
)
from app.dependencies import get_db
from app.utils.firebase_auth import verify_firebase_token

router = APIRouter(prefix="/favorites", tags=["Favorites"])


# ─────────────────────────────────────────────────────────────────────────────
# POST /favorites  → add a product to the current user’s favorites
# ─────────────────────────────────────────────────────────────────────────────
@router.post("/", response_model=FavoriteOut, status_code=status.HTTP_201_CREATED)
def create_fav(
    favorite: FavoriteCreate,                # expects only product_id from client
    db: Session = Depends(get_db),
    user=Depends(verify_firebase_token),     # provides user["uid"]
):
    # Inject uid so the CRUD layer has all it needs
    favorite.user_uid = user["uid"]          # type: ignore[attr-defined]
    return create_favorite(db, favorite)


# ─────────────────────────────────────────────────────────────────────────────
# GET /favorites  → list all favorites for the current user
# ─────────────────────────────────────────────────────────────────────────────
@router.get("/", response_model=List[FavoriteOut])
def list_my_favorites(
    db: Session = Depends(get_db),
    user=Depends(verify_firebase_token),
):
    return get_favorites_for_user(db, user["uid"])


# ─────────────────────────────────────────────────────────────────────────────
# DELETE /favorites/{product_id}  → un-favourite a product
# ─────────────────────────────────────────────────────────────────────────────
@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_fav(
    product_id: int,
    db: Session = Depends(get_db),
    user=Depends(verify_firebase_token),
):
    delete_favorite_by_product_and_user(db, product_id, user["uid"])
