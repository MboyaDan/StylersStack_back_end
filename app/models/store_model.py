# app/models/store_model.py

from sqlalchemy import Column, Integer, String, Text
from app.database import Base

class Store(Base):
    __tablename__ = "stores"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
