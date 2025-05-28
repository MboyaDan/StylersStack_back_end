from sqlalchemy.orm import Session, joinedload
from app.models.cart_model import Cart
from app.models.product_model import Product   # assuming this is the name
from app.schemas.cart_schema import CartCreate

def add_or_update_cart(db: Session, user_uid: str, body: CartCreate):
    cart = db.query(Cart).filter(
        Cart.user_uid == user_uid,
        Cart.product_id == body.productId
    ).first()

    if cart:
        cart.quantity += body.quantity
    else:
        cart = Cart(
            user_uid=user_uid,
            product_id=body.productId,
            quantity=body.quantity
        )
        db.add(cart)
    db.commit()
    db.refresh(cart)
    return cart

def get_cart_for_user(db: Session, user_uid: str):
    return (
        db.query(Cart)
        .options(joinedload(Cart.product))
        .filter(Cart.user_uid == user_uid)
        .all()
    )

def delete_cart_item(db: Session, user_uid: str, product_id: int):
    cart = db.query(Cart).filter(
        Cart.user_uid == user_uid,
        Cart.product_id == product_id
    ).first()
    if cart:
        db.delete(cart)
        db.commit()
    return cart
