#SQLAlchemy ORM class that defines how products are stored in the DB.
from sqlalchemy import Column, Integer, String, Text, Numeric, ForeignKey, TIMESTAMP, text, Float
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import relationship
from app.database import Base

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False)
    description = Column(Text)
    price = Column(Numeric(10, 2), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"))
    images = Column(ARRAY(Text))  # List of image URLs
    stock = Column(Integer, nullable=False, default=0)
    discount = Column(Float, nullable=True)
    rating = Column(Integer, default=0)
    sizes = Column(ARRAY(String), default=[])  # List of sizes (e.g., ['S', 'M'])
    colors = Column(ARRAY(Integer), default=[])  # List of int ARGB values
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))

    category = relationship("Category")
