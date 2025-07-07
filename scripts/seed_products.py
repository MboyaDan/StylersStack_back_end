from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timezone
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
        "name": "Canvas Shirts",
        "description": "Comfortable unisex sneakers for daily wear",
        "price": 45.50,
        "stock": 85,
        "images": ["https://via.placeholder.com/150"],
        "sizes": ["8", "9", "10", "11"],
        "colors": ["White", "Grey"],
        "rating": 4,
        "discount": 5.0,
        "category_name": "T-Shirt"
    },
    {
        "name": "Slim Fit Chinos",
        "description": "Modern cut chinos for casual or office wear",
        "price": 39.939,
        "stock": 200,
        "images": ["https://via.placeholder.com/150"],
        "sizes": ["30", "32", "34"],
        "colors": ["Khaki", "Navy"],
        "rating": 5,
        "discount": 15.0,
        "category_name": "Pant"
    },
    {
        "name": "Budget T-Shirt",
        "description": "Simple t-shirt for only 1 Ksh",
        "price": 1.00,
        "stock": 500,
        "images": ["https://via.placeholder.com/150"],
        "sizes": ["S", "M", "L"],
        "colors": ["White"],
        "rating": 3,
        "discount": 0.0,
        "category_name": "T-Shirt"
    },
    {
        "name": "Promo Pants",
        "description": "Special promo pants for only 1 Ksh",
        "price": 1.00,
        "stock": 300,
        "images": ["https://via.placeholder.com/150"],
        "sizes": ["30", "32"],
        "colors": ["Khaki"],
        "rating": 3,
        "discount": 0.0,
        "category_name": "Pant"
    },
    {
        "name": "Clearance Jacket",
        "description": "Clearance jacket at a throwaway price",
        "price": 1.00,
        "stock": 150,
        "images": ["https://via.placeholder.com/150"],
        "sizes": ["M", "L"],
        "colors": ["Blue"],
        "rating": 2,
        "discount": 0.0,
        "category_name": "Jacket"
    }
]

def seed_products():
    db: Session = SessionLocal()
    try:
        for data in product_seed_data:
            # Check if product already exists by name
            existing_product = db.query(Product).filter_by(name=data["name"]).first()
            if existing_product:
                print(f"ℹ️ Skipping '{data['name']}' - Already exists.")
                continue

            # Case-insensitive category lookup
            category = db.query(Category).filter(
                func.lower(Category.name) == data["category_name"].lower()
            ).first()
            

            if not category:
                print(f"⚠️ Skipping '{data['name']}' - Category '{data['category_name']}' not found.")
                continue

            # Convert color names to integer hex values
            try:
                color_values = [color_map[color] for color in data["colors"]]
            except KeyError as e:
                print(f"⚠️ Skipping '{data['name']}' - Unknown color: {e}")
                continue

            product_data = {
                **data,
                "category_id": category.id,
                "colors": color_values,
                "created_at": datetime.now(timezone.utc)
            }

            product_data.pop("category_name")

            product = Product(**product_data)
            db.add(product)
            print(f"✅ Added '{data['name']}' to category '{category.name}'")

        db.commit()
        print("✅ All products seeded successfully.")
    except Exception as e:
        db.rollback()
        print("❌ Error seeding products:", e)
    finally:
        db.close()

if __name__ == "__main__":
    seed_products()
