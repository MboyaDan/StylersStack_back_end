from sqlalchemy.orm import Session
from app.models.product_model import Product
from app.schemas.product_schema import ProductCreate

def create_product(db: Session, product: ProductCreate):
    db_product = Product(**product.dict())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

def get_products(db: Session):
    return db.query(Product).all()

def get_product_by_id(db: Session, product_id: int):
    return db.query(Product).filter(Product.id == product_id).first()

def update_product(db: Session, product_id: int, product: ProductCreate):
    db_product = db.query(Product).filter(Product.id == product_id).first()
    db_product.update(product.dict())
    db.commit()
    db.refresh(db_product)
    return db_product

def delete_product(db: Session, product_id: int):
    db_product = db.query(Product).filter(Product.id == product_id).first()
    db.delete(db_product)
    db.commit()
    return db_product