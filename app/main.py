#FastAPI entery point
from .database import Base,engine
from fastapi import FastAPI

from app.routes import product_routes,category_routes,cart_routes,favorite_routes
#create tables (if not already in DB)
Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(product_routes.router)
app.include_router(category_routes.router)
app.include_router(cart_routes.router)
app.include_router(favorite_routes.router)
@app.get("/")
def read_root():
    return {"message": "Welcome to the Fashion Backend API it up"}
