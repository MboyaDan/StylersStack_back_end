from sqlalchemy.orm import Session, joinedload
from app.models.favorite_model import Favorite
from app.schemas.favorite_schema import FavoriteOut
from fastapi import HTTPException

def get_favorites_for_user(db: Session, user_uid: str) -> list[FavoriteOut]:
    favorites = (
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


def delete_favorite_by_product_and_user(db: Session, product_id: int, user_uid: str):
    fav = (
        db.query(Favorite)
        .filter(Favorite.product_id == product_id, Favorite.user_uid == user_uid)
        .first()
    )

    if not fav:
        raise HTTPException(status_code=404, detail="Favorite not found")

    db.delete(fav)
    db.commit()
    return {"detail": "Favorite removed"}
