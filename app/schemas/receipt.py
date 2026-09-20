from datetime import datetime

from pydantic import BaseModel, ConfigDict

from schemas.common import Money


class ReceiptBase(BaseModel):
    sale_id: int
    receipt_number: str
    total_amount: Money


class ReceiptCreate(ReceiptBase):
    pass


class ReceiptUpdate(BaseModel):
    sale_id: int | None = None
    receipt_number: str | None = None
    total_amount: Money | None = None


class ReceiptRead(ReceiptBase):
    model_config = ConfigDict(from_attributes=True)

    receipt_id: int
    issue_date: datetime
