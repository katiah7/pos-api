from sqlalchemy import (
    Column, 
    DateTime, 
    ForeignKey, 
    Integer, 
    Numeric, 
    String, 
)

from sqlalchemy.orm import relationship
from database import Base

class Sale(Base):
    __tablename__="sales"

    sale_id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, ForeignKey("customers.customer_id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    sale_date = Column(DateTime, nullable=False)
    total_amount = Column(Numeric(10,2), nullable=False)
    payment_status = Column(String, nullable=False)
    customer = relationship("Customer", back_populates="sales")

    user = relationship("User", back_populates="sales")
    items = relationship("SaleItem", back_populates="sale")
    payment = relationship("Payment", back_populates="sale", uselist=False)
    receipt = relationship("Receipt", back_populates="sale", uselist=False)