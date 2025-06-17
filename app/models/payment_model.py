from sqlalchemy import Column, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database import Base

class Payment(Base):
    __tablename__ = "payments"

    id = Column(String, primary_key=True, index=True)  # ← Changed from Integer to String
    user_id = Column(String, ForeignKey("users.uid")) 
    order_id = Column(String, unique=True, index=True)
    amount = Column(Float)
    currency = Column(String, nullable=False)  
    phone_number = Column(String)
    payment_method = Column(String)  # 'mpesa', 'stripe', 'cod'
    payment_intent_id = Column(String, unique=True, nullable=True)  # For Stripe payments
    status = Column(String, default="pending")  # 'pending', 'succeeded', 'failed'
    created_at = Column(DateTime(timezone=True),default= lambda:datetime.now(timezone.utc))

    user = relationship("User", back_populates="payments")
