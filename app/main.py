from dotenv import load_dotenv
load_dotenv()

import os
from datetime import datetime
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from fastapi.templating import Jinja2Templates
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from app.limiter import limiter
from app.templates_engine import templates

from fastapi import Request, HTTPException
from fastapi.responses import RedirectResponse


from app.routes import (
    product_routes,
    category_routes,
    cart_routes,
    favorite_routes,
    address_router,
    payments_routes,
    user_router,
    admin_routes
)

app = FastAPI()

# --- Rate limiting middleware ---
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# --- Sessions (for admin login) ---
app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("SESSION_SECRET")
)

# --- Static files (e.g., Tailwind CSS, images) ---
app.mount("/static", StaticFiles(directory="app/static"), name="static")


# --- Include routers ---
app.include_router(product_routes.router)
app.include_router(category_routes.router)
app.include_router(cart_routes.router)
app.include_router(favorite_routes.router)
app.include_router(address_router.router)
app.include_router(payments_routes.router)
app.include_router(user_router.router)
app.include_router(admin_routes.router)

# --- Simple root route ---
@app.get("/")
def read_root():
    return {"message": "Welcome to the Fashion Backend API, it is up"}

@app.exception_handler(403)
async def forbidden_exception_handler(request: Request, exc: HTTPException):
    request.session["flash"] = "Please login to access the admin panel."
    return RedirectResponse(url="/admin/login", status_code=303)
