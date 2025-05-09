# app/models/promotion_model.py

from sqlalchemy import Column, Integer, String, Text, DateTime, Numeric
from sqlalchemy.sql import func
from app.database import Base

class Promotion(Base):
    __tablename__ = "promotions"

    id = Column(Integer, primary_key=True)
    title = Column(String(100), nullable=False)
    description = Column(Text)
    discount_percent = Column(Numeric(5, 2))  # e.g., 15.50%
    valid_until = Column(DateTime)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
