import re
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import Category

category_names = ["T-Shirt", "Pant", "Dress", "Jacket"]

def slugify(name: str) -> str:
    return re.sub(r'[^a-z0-9]+', '', name.lower())

def seed_categories():
    db: Session = SessionLocal()
    try:
        added = 0
        for name in category_names:
            slug = slugify(name)
            exists = db.query(Category).filter_by(slug=slug).first()
            if not exists:
                db.add(Category(name=name, slug=slug))
                added += 1
        db.commit()
        print(f"✅ Seed script completed. Categories added: {added}")
    except Exception as e:
        db.rollback()
        print("❌ Error seeding categories:", e)
    finally:
        db.close()

if __name__ == "__main__":
    print("⏳ Running seed script...")
    seed_categories()

