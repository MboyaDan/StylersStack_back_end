from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.schemas.category_schema import Category, CategoryCreate
from app.crud.category_crud import create_category, get_categories, get_category_by_name
from app.dependencies import get_db
from app.utils.firebase_auth import verify_firebase_token
from app.utils.slugify import generate_slug  # You’ll create this helper

router = APIRouter(prefix="/categories", tags=["Categories"])

@router.post("/", response_model=Category)
def create_new_category(
    category: CategoryCreate,
    db: Session = Depends(get_db),
    user=Depends(verify_firebase_token)
):
    # Check for existing category with same name
    existing = get_category_by_name(db, category.name)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category with this name already exists."
        )

    slug = generate_slug(category.name)
    return create_category(db, category, slug=slug)


@router.get("/", response_model=List[Category])
def read_categories(db: Session = Depends(get_db)):
    return get_categories(db)
