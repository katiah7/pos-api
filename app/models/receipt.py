from sqlalchemy import Column, DateTime, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class Receipt(Base):
    __tablename__ = "receipts"

    receipt_id = Column(Integer, primary_key=True, index=True)
    sale_id = Column(Integer, ForeignKey("sales.sale_id"), nullable=False, unique=True)
    receipt_number = Column(String, nullable=False, unique=True)
    issue_date = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    total_amount = Column(Numeric(10, 2), nullable=False)

    sale = relationship("Sale", back_populates="receipt")
