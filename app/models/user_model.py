from sqlalchemy import Column, String, DateTime
from sqlalchemy.sql import func
from app.database import Base
from sqlalchemy.orm import relationship
class User(Base):
    __tablename__ = "users"

    uid = Column(String, primary_key=True, index=True)  # Firebase UID
    email = Column(String, unique=True, index=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    address = relationship("Address", back_populates="user", uselist=False)
    

