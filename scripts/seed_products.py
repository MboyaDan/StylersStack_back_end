from sqlalchemy.orm import Session
from datetime import datetime
from app.database import SessionLocal
from app.models import Product, Category

# Mapping of color names to hex codes
color_map = {
    "Black": 0x000000,
    "White": 0xFFFFFF,
    "Blue": 0x0000FF,
    "Grey": 0x808080,
    "Khaki": 0xF0E68C,
    "Navy": 0x000080,
}

# Product seed data with category_name instead of hardcoded ID
product_seed_data = [
    {
        "name": "Denim Jacket",
        "description": "Stylish blue denim with a vintage cut",
        "price": 59.99,
        "stock": 120,
        "images": ["https://via.placeholder.com/150"],
        "sizes": ["S", "M", "L"],
        "colors": ["Blue", "Black"],
        "rating": 4,
        "discount": 10.0,
        "category_name": "Jacket"
    },
    {
        "name": "Canvas Sneakers",
        "description": "Comfortable unisex sneakers for daily wear",
        "price": 45.50,
        "stock": 85,
        "images": ["https://via.placeholder.com/150"],
        "sizes": ["8", "9", "10", "11"],
        "colors": ["White", "Grey"],
        "rating": 4,
        "discount": 5.0,
        "category_name": "T-Shirt"  # Adjust this as needed
    },
    {
        "name": "Slim Fit Chinos",
        "description": "Modern cut chinos for casual or office wear",
        "price": 39.99,
        "stock": 200,
        "images": ["https://via.placeholder.com/150"],
        "sizes": ["30", "32", "34"],
        "colors": ["Khaki", "Navy"],
        "rating": 5,
        "discount": 15.0,
        "category_name": "Pant"
    }
]

def seed_products():
    db: Session = SessionLocal()
    try:
        for data in product_seed_data:
            category = db.query(Category).filter_by(name=data["category_name"]).first()
            if not category:
                print(f"⚠️ Skipping '{data['name']}' - Category '{data['category_name']}' not found.")
                continue

            product_data = {
                **data,
                "category_id": category.id,
                "colors": [color_map[c] for c in data["colors"]],
                "created_at": datetime.utcnow()
            }

            # Remove category_name from the final product fields
            product_data.pop("category_name")

            product = Product(**product_data)
            db.add(product)

        db.commit()
        print("✅ Products seeded successfully.")
    except Exception as e:
        db.rollback()
        print("❌ Error seeding products:", e)
    finally:
        db.close()

if __name__ == "__main__":
    seed_products()
