from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.schemas.category_schema import Category, CategoryCreate
from app.crud.category_crud import create_category, get_categories
from app.dependencies import get_db
from app.utils.firebase_auth import verify_firebase_token
router = APIRouter(prefix="/categories", tags=["Categories"])

@router.post("/", response_model=Category)
def create(category: CategoryCreate, db: Session = Depends(get_db),user=Depends(verify_firebase_token)):
    return create_category(db, category)

@router.get("/", response_model=List[Category])
def read_all(db: Session = Depends(get_db)):
    return get_categories(db)
