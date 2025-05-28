# app/crud/favorite_crud.py
from __future__ import annotations

from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status

from app.models.favorite_model import Favorite
from app.models.product_model import Product          # ← adjust path if needed
from app.schemas.favorite_schema import FavoriteCreate, FavoriteOut


# ────────────────────────────────────────────────────────────────────────────
# CREATE
# ────────────────────────────────────────────────────────────────────────────
def create_favorite(
    db: Session,
    payload: FavoriteCreate,
) -> FavoriteOut:
    """Add a product to a user’s favorites (idempotent)."""

    # 1) Verify product exists
    product: Product | None = (
        db.query(Product).filter(Product.id == payload.product_id).first()
    )
    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )

    # 2) Check for existing favorite (unique per user+product)
    fav: Favorite | None = (
        db.query(Favorite)
        .filter(
            Favorite.product_id == payload.product_id,
            Favorite.user_uid == payload.user_uid,
        )
        .first()
    )
    if fav is None:
        # 3) Create new favorite
        fav = Favorite(user_uid=payload.user_uid, product_id=payload.product_id)
        db.add(fav)
        try:
            db.commit()
        except IntegrityError:
            # Unique constraint race condition (just in case)
            db.rollback()
        db.refresh(fav)
    else:
        # Already exists → no-op
        pass

    # 4) Build response
    return FavoriteOut(
        productId=str(product.id),
        productName=product.name,
        imageUrl=product.images[0] if product.images else "",
        price=float(product.price),
        userId=fav.user_uid,
    )


# ────────────────────────────────────────────────────────────────────────────
# READ (all favorites for a user)
# ────────────────────────────────────────────────────────────────────────────
def get_favorites_for_user(
    db: Session,
    user_uid: str,
) -> list[FavoriteOut]:
    favorites: list[Favorite] = (
        db.query(Favorite)
        .options(joinedload(Favorite.product))
        .filter(Favorite.user_uid == user_uid)
        .all()
    )

    return [
        FavoriteOut(
            productId=str(fav.product.id),
            productName=fav.product.name,
            imageUrl=fav.product.images[0] if fav.product.images else "",
            price=float(fav.product.price),
            userId=fav.user_uid,
        )
        for fav in favorites
    ]


# ────────────────────────────────────────────────────────────────────────────
# DELETE
# ────────────────────────────────────────────────────────────────────────────
def delete_favorite_by_product_and_user(
    db: Session,
    product_id: int,
    user_uid: str,
) -> dict[str, str]:
    fav: Favorite | None = (
        db.query(Favorite)
        .filter(Favorite.product_id == product_id, Favorite.user_uid == user_uid)
        .first()
    )

    if fav is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Favorite not found",
        )

    db.delete(fav)
    db.commit()
    return {"detail": "Favorite removed"}
