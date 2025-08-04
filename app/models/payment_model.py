from sqlalchemy import Column, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database import Base

class Payment(Base):
    __tablename__ = "payments"

    payment_intent_id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.uid"))
    amount = Column(Float, nullable=False)
    currency = Column(String, nullable=False)
    phone_number = Column(String, nullable=False)
    payment_method = Column(String, nullable=False)
    status = Column(String, default="pending")
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    checkout_request_id = Column(String, nullable=True)

    # Relationships
    user = relationship("User", back_populates="payments")
    order = relationship("Order", back_populates="payment", uselist=False)
