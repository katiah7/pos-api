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


class Receipt(Base):
    __tablename__="receipts"

    receipt_id = Column(Integer, primary_key=True)
    sale_id = Column(Integer, ForeignKey("sales.sale_id"), unique=True)
    receipt_number = Column(String, nullable=False)
    issue_date = Column(DateTime, nullable=False)
    total_amount = Column(Numeric(10,2), nullable=False)

    sale = relationship("Sale", back_populates="receipt"
    )