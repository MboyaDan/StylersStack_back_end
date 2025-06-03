from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    order_id = Column(String, unique=True, index=True)
    amount = Column(Float)
    phone_number = Column(String)
    payment_method = Column(String)  # 'mpesa', 'stripe', 'cod'
    status = Column(String, default="pending")  # 'pending', 'succeeded', 'failed'
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="payments")
