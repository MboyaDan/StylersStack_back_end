from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.database import Base

class Favorite(Base):
    __tablename__ = "favorites"

    id = Column(Integer, primary_key=True)
    user_uid = Column(String, ForeignKey("users.uid", ondelete="CASCADE"))
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"))

    __table_args__ = (
        UniqueConstraint('user_uid', 'product_id', name='uq_fav_user_product'),
    )

    product = relationship("Product")
    user = relationship("User")
