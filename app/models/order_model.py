# app/models/order_model.py

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True)
    user_uid = Column(String, ForeignKey("users.uid"))
    total_amount = Column(Numeric(10, 2), nullable=False)
    status = Column(String, default="pending")  # e.g. pending, paid, delivered
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User")
