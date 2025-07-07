from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from typing import List
from app.schemas.product_schema import Product as ProductOut, ProductCreate
from app.crud.product_crud import (
    create_product, get_products,
    get_product_by_id, update_product,
    delete_product
)
from app.dependencies import get_db
from app.utils.firebase_auth import verify_firebase_token
from app.limiter import limiter
from app.utils.cache import get_cache, set_cache, delete_cache
import os
import asyncio
from fastapi import Form, File, UploadFile
from app.utils.firebase_upload import upload_image_to_firebase
from app.models.product_model import Product
from app.schemas.product_schema import Product as ProductOut

from sqlalchemy.exc import SQLAlchemyError

router = APIRouter(prefix="/products", tags=["Products"])

@router.post("/", response_model=ProductOut)
@limiter.limit(os.getenv("RATE_LIMIT"))
def create(
    request: Request,  
    product: ProductCreate,
    db: Session = Depends(get_db),
    user=Depends(verify_firebase_token)
):
    created = create_product(db, product)
    asyncio.create_task(delete_cache("products:all"))
    return ProductOut.model_validate(created)

@router.get("/", response_model=List[ProductOut])
@limiter.limit(os.getenv("RATE_LIMIT"))
async def read_all(
    request: Request,
    db: Session = Depends(get_db),
    user=Depends(verify_firebase_token)
):
    cache_key = "products:all"
    cached = await get_cache(cache_key)
    if cached:
        return cached

    result = get_products(db)
    pydantic_products = [ProductOut.model_validate(product) for product in result]
    await set_cache(cache_key, [p.model_dump() for p in pydantic_products])
    return pydantic_products

@router.get("/{product_id}", response_model=ProductOut)
@limiter.limit(os.getenv("RATE_LIMIT"))
async def read_by_id(
    request: Request,
    product_id: int,
    db: Session = Depends(get_db),
    user=Depends(verify_firebase_token)
):
    cache_key = f"product:{product_id}"
    cached = await get_cache(cache_key)
    if cached:
        return cached

    result = get_product_by_id(db, product_id)
    pydantic_product = ProductOut.model_validate(result)
    await set_cache(cache_key, pydantic_product.model_dump())
    return pydantic_product

@router.put("/{product_id}", response_model=ProductOut)
@limiter.limit(os.getenv("RATE_LIMIT"))
def update(
    request: Request,
    product_id: int,
    product: ProductCreate,
    db: Session = Depends(get_db),
    user=Depends(verify_firebase_token)
):
    updated = update_product(db, product_id, product)
    asyncio.create_task(delete_cache(f"product:{product_id}"))
    asyncio.create_task(delete_cache("products:all"))
    return ProductOut.model_validate(updated)

@router.delete("/{product_id}", response_model=ProductOut)
@limiter.limit(os.getenv("RATE_LIMIT"))
def delete(
    request: Request,
    product_id: int,
    db: Session = Depends(get_db),
    user=Depends(verify_firebase_token)
):
    deleted = delete_product(db, product_id)
    asyncio.create_task(delete_cache(f"product:{product_id}"))
    asyncio.create_task(delete_cache("products:all"))
    return ProductOut.model_validate(deleted)

