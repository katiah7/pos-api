from datetime import datetime
from pydantic import BaseModel, ConfigDict

class ReceiptBase(BaseModel):
    sale_id: int
    receipt_number: str
    issue_date: datetime
    total_amount: float

class ReceiptCreate(ReceiptBase):
    pass

class ReceiptUpdate(BaseModel):
    receipt_number: str | None = None
    issue_date: datetime | None = None
    total_amount: float | None = None

class ReceiptResponse(ReceiptBase):
    receipt_id: int

    model_config = ConfigDict(
        from_attributes=True
    )