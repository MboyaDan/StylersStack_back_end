from sqlalchemy import Column, Integer, String, Text, Numeric, ForeignKey, TIMESTAMP
from sqlalchemy.orm import relationship
from app.database import Base

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False)
    description = Column(Text)
    price = Column(Numeric(10, 2), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"))
    image_url = Column(Text)
    created_at = Column(TIMESTAMP, server_default="CURRENT_TIMESTAMP")

    category = relationship("Category")
