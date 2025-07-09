from sqlalchemy import Column, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database import Base

class Payment(Base):
    __tablename__ = "payments"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.uid")) 
    order_id = Column(String, ForeignKey("orders.id"), index=True)  
    amount = Column(Float)
    currency = Column(String, nullable=False)  
    phone_number = Column(String)
    payment_method = Column(String)
    payment_intent_id = Column(String, unique=True, nullable=True)
    status = Column(String, default="pending")
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    checkout_request_id = Column(String, nullable=True)

    user = relationship("User", back_populates="payments")
    order = relationship("Order", back_populates="payments")

