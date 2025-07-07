from fastapi import (
    APIRouter, Depends, Request, Form, File, UploadFile, HTTPException
)
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from firebase_admin import auth as firebase_auth

from app.dependencies import get_db
from app.models.product_model import Product
from app.models.category_model import Category
from app.utils.cloudinary_upload import upload_image_to_cloudinary

router = APIRouter(prefix="/admin", tags=["Admin"])
templates = Jinja2Templates(directory="app/templates")


# 🔐 Protect admin routes
def require_admin(request: Request):
    if not request.session.get("user"):
        raise HTTPException(status_code=403, detail="Unauthorized")
    return request.session["user"]


# 🚪 Admin Login Page
@router.get("/login")
def login_form(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


# 🔑 Handle Login
@router.post("/login")
def login(request: Request, id_token: str = Form(...)):
    try:
        decoded_token = firebase_auth.verify_id_token(id_token)
        request.session["user"] = decoded_token
        return RedirectResponse(url="/admin/dashboard", status_code=303)
    except Exception:
        return templates.TemplateResponse("login.html", {
            "request": request,
            "error": "Invalid token. Try again."
        })


# 📊 Admin Dashboard – only active products
@router.get("/dashboard")
def admin_dashboard(
    request: Request,
    db: Session = Depends(get_db),
    user=Depends(require_admin)
):
    products = db.query(Product).filter(Product.is_archived == False).order_by(Product.id.desc()).all()
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "products": products
    })


# 🗃️ Archived Products View
@router.get("/archived-products")
def archived_products(
    request: Request,
    db: Session = Depends(get_db),
    user=Depends(require_admin)
):
    archived = db.query(Product).filter(Product.is_archived == True).order_by(Product.id.desc()).all()
    return templates.TemplateResponse("archived_products.html", {
        "request": request,
        "products": archived
    })


# 🧾 Product Creation Form
@router.get("/products/new")
def new_product_form(
    request: Request,
    db: Session = Depends(get_db),
    user=Depends(require_admin)
):
    categories = db.query(Category).all()
    return templates.TemplateResponse("product_form.html", {
        "request": request,
        "categories": categories
    })


# ⬆️ Upload Product Handler
@router.post("/products/new")
async def upload_product(
    request: Request,
    name: str = Form(...),
    description: str = Form(...),
    price: float = Form(...),
    category_id: int = Form(...),
    stock: int = Form(...),
    sizes: str = Form(...),
    colors: str = Form(...),
    discount: float = Form(None),
    rating: int = Form(0),
    image: UploadFile = File(...),
    db: Session = Depends(get_db),
    user=Depends(require_admin)
):
    try:
        image_url = upload_image_to_cloudinary(image.file, image.filename)

        sizes_list = [s.strip() for s in sizes.split(",") if s.strip()]
        colors_list = [int(c.strip()) for c in colors.split(",") if c.strip().isdigit()]

        new_product = Product(
            name=name,
            description=description,
            price=price,
            category_id=category_id,
            stock=stock,
            discount=discount,
            rating=rating,
            sizes=sizes_list,
            colors=colors_list,
            images=[image_url]
        )

        db.add(new_product)
        db.commit()
        db.refresh(new_product)

        request.session["flash"] = "Product added successfully!"
        return RedirectResponse(url="/admin/dashboard", status_code=303)

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


# 📂 View & Add Categories
@router.get("/categories", response_class=HTMLResponse)
def view_categories(
    request: Request,
    db: Session = Depends(get_db),
    user=Depends(require_admin)
):
    categories = db.query(Category).order_by(Category.id.desc()).all()
    return templates.TemplateResponse("categories.html", {
        "request": request,
        "categories": categories
    })


@router.post("/categories/new")
def create_category(
    request: Request,
    name: str = Form(...),
    db: Session = Depends(get_db),
    user=Depends(require_admin)
):
    try:
        new_category = Category(name=name.strip())
        db.add(new_category)
        db.commit()
        request.session["flash"] = "Category added successfully!"
    except Exception as e:
        db.rollback()
        request.session["flash"] = f"Error: {str(e)}"

    return RedirectResponse(url="/admin/categories", status_code=303)


# 📝 Edit Product Form
@router.get("/products/{product_id}/edit")
def edit_product_form(
    product_id: int,
    request: Request,
    db: Session = Depends(get_db),
    user=Depends(require_admin)
):
    product = db.query(Product).get(product_id)
    categories = db.query(Category).all()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    return templates.TemplateResponse("product_form.html", {
        "request": request,
        "product": product,
        "categories": categories,
        "editing": True,
    })


# ⬆️ Update Product Handler
@router.post("/products/{product_id}/edit")
async def update_product(
    product_id: int,
    request: Request,
    name: str = Form(...),
    description: str = Form(...),
    price: float = Form(...),
    category_id: int = Form(...),
    stock: int = Form(...),
    sizes: str = Form(...),
    colors: str = Form(...),
    discount: float = Form(None),
    rating: int = Form(0),
    image: UploadFile = File(None),
    db: Session = Depends(get_db),
    user=Depends(require_admin)
):
    product = db.query(Product).get(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    try:
        product.name = name
        product.description = description
        product.price = price
        product.category_id = category_id
        product.stock = stock
        product.discount = discount
        product.rating = rating
        product.sizes = [s.strip() for s in sizes.split(",") if s.strip()]
        product.colors = [int(c.strip()) for c in colors.split(",") if c.strip().isdigit()]

        if image:
            product.images = [upload_image_to_cloudinary(image.file, image.filename)]

        db.commit()
        request.session["flash"] = "Product updated successfully!"
        return RedirectResponse(url="/admin/dashboard", status_code=303)

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Update failed: {str(e)}")


# 🗑️ Archive (Soft Delete) Product
@router.get("/products/{product_id}/delete")
def archive_product(
    product_id: int,
    request: Request,
    db: Session = Depends(get_db),
    user=Depends(require_admin)
):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    product.is_archived = True
    db.commit()

    request.session["flash"] = "Product archived successfully!"
    return RedirectResponse(url="/admin/dashboard", status_code=303)


# 🔁 Restore Archived Product
@router.get("/products/{product_id}/restore")
def restore_product(
    product_id: int,
    request: Request,
    db: Session = Depends(get_db),
    user=Depends(require_admin)
):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    product.is_archived = False
    db.commit()

    request.session["flash"] = "Product restored successfully!"
    return RedirectResponse(url="/admin/archived-products", status_code=303)
