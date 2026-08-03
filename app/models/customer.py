from sqlalchemy import (
    Column, 
    Integer,  
    String, 
)

from sqlalchemy.orm import relationship
from database import Base


class Customer(Base):
    __tablename__ = "customers"

    customer_id = Column(Integer, primary_key=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    phone = Column(String, nullable=False)
    email = Column(String, nullable=False)
    loyalty_points = Column(Integer, default=0)

    sales = relationship("Sale", back_populates="customer")