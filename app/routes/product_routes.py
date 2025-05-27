from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.schemas.product_schema import Product, ProductCreate
from app.crud.product_crud import create_product, get_products,get_product_by_id,update_product,delete_product
from app.dependencies import get_db
from app.utils.firebase_auth import verify_firebase_token


router = APIRouter(prefix="/products", tags=["Products"])

#   Adding Auth Dependency to our Routes      

@router.post("/", response_model=Product)
def create(product: ProductCreate, db: Session = Depends(get_db),user=Depends(verify_firebase_token)):
    return create_product(db, product)

@router.get("/", response_model=List[Product])
def read_all(db: Session = Depends(get_db),user= Depends(verify_firebase_token)):
    return get_products(db)

@router.get("/{product_id}", response_model=Product)
def read_by_id(product_id: int, db: Session = Depends(get_db),user= Depends(verify_firebase_token)):
    return get_product_by_id(db, product_id)

@router.put("/{product_id}", response_model=Product)
def update(product_id: int, product: ProductCreate, db: Session = Depends(get_db),user= Depends(verify_firebase_token)):
    return update_product(db, product_id, product)

@router.delete("/{product_id}", response_model=Product)
def delete(product_id: int, db: Session = Depends(get_db),user= Depends(verify_firebase_token)):
    return delete_product(db, product_id)
