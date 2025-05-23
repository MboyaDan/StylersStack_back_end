from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import Category

category_names = ["tshirt", "pant", "dress", "jacket"]  


def seed_categories():
    db: Session = SessionLocal()
    try:
        added = 0
        for name in category_names:
            exists = db.query(Category).filter_by(name=name).first()
            if not exists:
                db.add(Category(name=name))
                added += 1
        db.commit()
        if added:
            print(f"✅ {added} categories seeded successfully.")
        else:
            print("ℹ️ Categories already exist. Nothing to seed.")
    except Exception as e:
        db.rollback()
        print("❌ Error seeding categories:", e)
    finally:
        db.close()

if __name__ == "__main__":
    print("⏳ Starting seeding...")
    seed_categories()
