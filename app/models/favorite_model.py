# app/models/favorite_model.py

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class Favorite(Base):
    __tablename__ = "favorites"

    id = Column(Integer, primary_key=True)
    user_uid = Column(String, ForeignKey("users.uid"))
    product_id = Column(Integer, ForeignKey("products.id"))

    product = relationship("Product")
    user = relationship("User")
