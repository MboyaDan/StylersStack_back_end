from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint, DateTime, func
from sqlalchemy.orm import relationship
from app.database import Base

class Cart(Base):
    __tablename__ = "carts"

    id         = Column(Integer, primary_key=True)
    user_uid   = Column(String, ForeignKey("users.uid"))
    product_id = Column(Integer, ForeignKey("products.id"))
    quantity   = Column(Integer, default=1)
    added_at   = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        UniqueConstraint("user_uid", "product_id", name="user_product_unique"),
    )

    product = relationship("Product")   # gives you product.name, price, image, …
    user    = relationship("User")
