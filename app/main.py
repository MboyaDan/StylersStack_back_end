# app/main.py

from dotenv import load_dotenv
load_dotenv()

import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from fastapi.templating import Jinja2Templates
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from app.limiter import limiter

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

# --- Middleware ---
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Session support for admin login
app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("SESSION_SECRET")
)
#  Static files (Tailwind CSS/JS)
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Register API & Admin routers
app.include_router(product_routes.router)
app.include_router(category_routes.router)
app.include_router(cart_routes.router)
app.include_router(favorite_routes.router)
app.include_router(address_router.router)
app.include_router(payments_routes.router)
app.include_router(user_router.router)
app.include_router(admin_routes.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Fashion Backend API, it is up"}
