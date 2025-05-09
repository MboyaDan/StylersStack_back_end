from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.schemas.product_schema import Product, ProductCreate
from app.crud.product_crud import create_product, get_products
from app.database import get_db
from app.utils. firebase_auth import verify_firebase_token


router = APIRouter(prefix="/products", tags=["Products"])

# Adding Auth Dependency to our Routes

@router.post("/", response_model=Product)
def create(product: ProductCreate, db: Session = Depends(get_db),user=Depends(verify_firebase_token)):
    return create_product(db, product)

@router.get("/", response_model=List[Product])
def read_all(db: Session = Depends(get_db),user= Depends(verify_firebase_token)):
    return get_products(db)
