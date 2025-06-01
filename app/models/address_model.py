from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.database import Base

class Address(Base):
    __tablename__ = "addresses"

    id        = Column(Integer, primary_key=True, index=True)
    user_uid  = Column(String, ForeignKey("users.uid"), nullable=False)
    address   = Column(String(255), nullable=False)

    __table_args__ = (
        UniqueConstraint("user_uid", name="uc_user_address"),
    )

    user = relationship("User", back_populates="address")



   