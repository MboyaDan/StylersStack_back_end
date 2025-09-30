# create_admin.py
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from database import SessionLocal
from models import User  # adjust if your user model is named differently

# Password hashing setup
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_admin():
    db: Session = SessionLocal()

    email = "admin@example.com"
    password = "admin123"   # change to a strong one later

    # Check if admin already exists
    existing_user = db.query(User).filter(User.email == email).first()
    if existing_user:
        print("✅ Admin user already exists:", email)
        return

    hashed_password = pwd_context.hash(password)
    new_user = User(
        email=email,
        password=hashed_password,
        is_admin=True   # make sure your User model has this field
    )
    db.add(new_user)
    db.commit()
    print(f"✅ Admin created: {email} / {password}")

if __name__ == "__main__":
    create_admin()
