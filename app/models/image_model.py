# app/models/image_model.py

from sqlalchemy import Column, Integer, String, ForeignKey
from app.database import Base

class UploadedImage(Base):
    __tablename__ = "uploaded_images"

    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey("products.id"))
    url = Column(String, nullable=False)
