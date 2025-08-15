from fastapi import (
    APIRouter, Depends, Request, Form, File, UploadFile, HTTPException
)
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from firebase_admin import auth as firebase_auth
from app.templates_engine import templates
from app.models.order_model import Order
from app.models.payment_model import Payment
from fastapi import Query
from datetime import datetime, timedelta
from app.models.order_item_model import OrderItem
from app.models.user_model import User
from sqlalchemy import func
from sqlalchemy.orm import joinedload


from app.dependencies import get_db
from app.models.product_model import Product
from app.models.category_model import Category
from app.utils.cloudinary_upload import upload_image_to_cloudinary
from app.dependencies import require_admin

router = APIRouter(prefix="/admin", tags=["Admin"])



# Admin Login Page
@router.post("/login")
def login(request: Request, id_token: str = Form(...)):
    try:
        decoded_token = firebase_auth.verify_id_token(id_token)
        request.session["user"] = decoded_token
        request.session["flash"] = "Welcome back, admin!"
        return RedirectResponse(url="/admin/dashboard", status_code=303)
    except Exception:
        request.session["flash"] = "Invalid login. Please try again."
        return RedirectResponse(url="/admin/login", status_code=303)

@router.get("/login")
def login_form(request: Request):
    flash = request.session.pop("flash", None)
    return templates.TemplateResponse("login.html", {
        "request": request,
        "flash": flash
    })

@router.post("/logout")
def admin_logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/admin/login", status_code=303)




@router.get("/favicon.ico")
def favicon():
    return RedirectResponse(url="/static/favicon.ico")  


# Admin Dashboard 
@router.get("/dashboard")
def admin_dashboard(
    request: Request,
    db: Session = Depends(get_db),
    user=Depends(require_admin)
):
    total_products = db.query(Product).filter(Product.is_archived == False).count()
    archived_products = db.query(Product).filter(Product.is_archived == True).count()
    low_stock = db.query(Product).filter(Product.stock < 5, Product.is_archived == False).count()
    total_orders = db.query(Order).count()
    total_users = db.query(User).count()

    # Total revenue from completed payments
    total_revenue = db.query(Payment).filter(Payment.status == "completed").with_entities(func.sum(Payment.amount)).scalar() or 0

    # Recent 5 orders
    recent_orders = db.query(Order).order_by(Order.created_at.desc()).limit(5).all()

    # Sales data for last 7 days
    from datetime import datetime, timedelta
    today = datetime.utcnow().date()
    last_7_days = [(today - timedelta(days=i)) for i in range(6, -1, -1)]
    revenue_by_day = []

    for day in last_7_days:
        day_total = db.query(Payment).filter(
            Payment.status == "completed",
            func.date(Payment.created_at) == day
        ).with_entities(func.sum(Payment.amount)).scalar() or 0
        revenue_by_day.append({"date": day.strftime("%a"), "total": float(day_total)})

    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "total_products": total_products,
        "archived_products": archived_products,
        "low_stock": low_stock,
        "total_orders": total_orders,
        "total_users": total_users,
        "total_revenue": total_revenue,
        "recent_orders": recent_orders,
        "revenue_by_day": revenue_by_day
    })



# Product Creation Form
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


# Upload Product Handler
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
        return RedirectResponse(url="/admin/products", status_code=303)

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


# View & Add Categories
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


# Edit Product Form
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


#Update Product Handler
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

# Archived Products View
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


#  Archive (Soft Delete) Product
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
    return RedirectResponse(url="/admin/products", status_code=303)


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

# 🚨 Permanently Delete Product (Only allowed if archived)
@router.get("/products/{product_id}/hard-delete")
def hard_delete_product(
    product_id: int,
    request: Request,
    db: Session = Depends(get_db),
    user=Depends(require_admin)
):
    product = db.query(Product).filter(Product.id == product_id, Product.is_archived == True).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found or not archived")

    db.delete(product)
    db.commit()

    request.session["flash"] = "Product permanently deleted."
    return RedirectResponse(url="/admin/archived-products", status_code=303)


# 🗂️ Orders and Payments Management



@router.get("/orders", response_class=HTMLResponse)
def admin_orders(
    request: Request,
    db: Session = Depends(get_db),
    status: str = Query(default=None),
    start_date: str = Query(default=None),
    end_date: str = Query(default=None),
    user=Depends(require_admin)
):
    query = db.query(Order)

    if status:
        query = query.filter(Order.status == status)

    if start_date:
        try:
            start = datetime.strptime(start_date, "%Y-%m-%d")
            query = query.filter(Order.created_at >= start)
        except ValueError:
            pass

    if end_date:
        try:
            end = datetime.strptime(end_date, "%Y-%m-%d")
            query = query.filter(Order.created_at <= end)
        except ValueError:
            pass

    orders = query.order_by(Order.created_at.desc()).all()
    return templates.TemplateResponse("orders.html", {
        "request": request,
        "orders": orders
    })



@router.get("/payments", response_class=HTMLResponse)
def admin_payments(
    request: Request,
    db: Session = Depends(get_db),
    status: str = Query(default=None),
    method: str = Query(default=None),
    user=Depends(require_admin)
):
    query = db.query(Payment)

    if status:
        query = query.filter(Payment.status == status)

    if method:
        query = query.filter(Payment.payment_method == method)

    payments = query.order_by(Payment.created_at.desc()).all()
    return templates.TemplateResponse("payments.html", {
        "request": request,
        "payments": payments
    })

@router.get("/orders/{order_id}", response_class=HTMLResponse)
async def admin_order_detail(request: Request, order_id: str, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    payment = db.query(Payment).filter(Payment.user_id == str(order.id)).first()

    # Optional: Order items, if you have a table for that
    items = db.query(OrderItem).filter(OrderItem.order_id == order.id).all() if hasattr(Order, "items") else []

    return templates.TemplateResponse("order_detail.html", {
        "request": request,
        "order": order,
        "payment": payment,
        "items": items
    })



@router.get("/users/{uid}", response_class=HTMLResponse)
def admin_user_detail(uid: str, request: Request, db: Session = Depends(get_db)):
    user = db.query(User)\
        .options(joinedload(User.address), joinedload(User.payments), joinedload(User.orders))\
        .filter(User.uid == uid).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return templates.TemplateResponse("user_details.html", {
        "request": request,
        "user": user
    })


@router.get("/users", response_class=HTMLResponse)
def admin_user_list(request: Request, db: Session = Depends(get_db), user=Depends(require_admin)):
    users = db.query(User).order_by(User.created_at.desc()).all()
    return templates.TemplateResponse("user_list.html", {
        "request": request,
        "users": users
    })

@router.get("/products", response_class=HTMLResponse)
def admin_products_page(
    request: Request,
    db: Session = Depends(get_db),
    user=Depends(require_admin)
):
    search = request.query_params.get("search", "")
    category_id = request.query_params.get("category")

    query = db.query(Product).filter(Product.is_archived == False)

    if search:
        query = query.filter(Product.name.ilike(f"%{search}%"))
    if category_id:
        try:
            query = query.filter(Product.category_id == int(category_id))
        except ValueError:
            pass  # If category_id is not an integer

    products = query.order_by(Product.id.desc()).all()
    categories = db.query(Category).order_by(Category.name).all()

    return templates.TemplateResponse("products.html", {
        "request": request,
        "products": products,
        "categories": categories,
    })

