# FastAPI entry point

from dotenv import load_dotenv
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from app.limiter import limiter

load_dotenv() 

from fastapi import FastAPI
from .database import Base, engine
from app.routes import (
    product_routes,
    category_routes,
    cart_routes,
    favorite_routes,
    address_router,
    payments_routes,
    user_router,
    test_routes
)

# Create tables (if not already in DB)
#Base.metadata.create_all(bind=engine)

app = FastAPI()
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Register routes
app.include_router(product_routes.router)
app.include_router(category_routes.router)
app.include_router(cart_routes.router)
app.include_router(favorite_routes.router)
app.include_router(address_router.router)
app.include_router(payments_routes.router)
app.include_router(user_router.router)
app.include_router(test_routes.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Fashion Backend API, it is up"}
