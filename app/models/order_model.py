from sqlalchemy import Column, String, ForeignKey, DateTime, Numeric, func
from sqlalchemy.orm import relationship
from app.database import Base

class Order(Base):
    __tablename__ = "orders"

    id = Column(String, primary_key=True)  # e.g., "ORD-1750939705415"
    user_uid = Column(String, ForeignKey("users.uid"))
    total_amount = Column(Numeric(10, 2), nullable=False)
    status = Column(String, default="pending")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    payment_id = Column(String, ForeignKey("payments.payment_intent_id"), unique=True, nullable=False)

    # Relationships
    user = relationship("User", back_populates="orders")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    payment = relationship("Payment", back_populates="order", uselist=False)
