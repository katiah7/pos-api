from sqlalchemy import (
    Boolean, 
    Column, 
    DateTime, 
    ForeignKey, 
    Integer, 
    Numeric, 
    String, 
)

from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from database import Base

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    product_name = Column(String, nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    supplier_id = Column(Integer, ForeignKey("supplier.id"), nullable=True)
    brand = Column(String, nullable=False)
    price = Column(Numeric(10,2), nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now)

    category = relationship("Category", back_populates="products")
    supplier = relationship("Supplier", back_populates="products")
    inventory = relationship(
        "Inventory", back_populates="product", useList=False
    )
