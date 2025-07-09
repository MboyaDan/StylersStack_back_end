# app/models/order_model.py

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
from app.models.payment_model import Payment  
from app.models.order_item_model import OrderItem 
class Order(Base):
    __tablename__ = "orders"

    id = Column(String, primary_key=True)
    user_uid = Column(String, ForeignKey("users.uid"))
    total_amount = Column(Numeric(10, 2), nullable=False)
    status = Column(String, default="pending")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="orders")

    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    payments = relationship("Payment", back_populates="order", cascade="all, delete-orphan") 

