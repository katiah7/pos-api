from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict

from schemas.common import Money

PaymentStatus = Literal["paid", "unpaid"]


class SaleBase(BaseModel):
    customer_id: int
    user_id: int
    total_amount: Money
    payment_status: PaymentStatus = "unpaid"


class SaleCreate(SaleBase):
    pass


class SaleUpdate(BaseModel):
    customer_id: int | None = None
    user_id: int | None = None
    total_amount: Money | None = None
    payment_status: PaymentStatus | None = None


class SaleRead(SaleBase):
    model_config = ConfigDict(from_attributes=True)

    sale_id: int
    sale_date: datetime
