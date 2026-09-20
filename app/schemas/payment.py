from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict

from schemas.common import Money

PaymentMethod = Literal["cash", "mpesa", "card", "crypto"]


class PaymentBase(BaseModel):
    sale_id: int
    payment_method: PaymentMethod
    amount_paid: Money
    transaction_reference: str


class PaymentCreate(PaymentBase):
    pass


class PaymentUpdate(BaseModel):
    sale_id: int | None = None
    payment_method: PaymentMethod | None = None
    amount_paid: Money | None = None
    transaction_reference: str | None = None


class PaymentRead(PaymentBase):
    model_config = ConfigDict(from_attributes=True)

    payment_id: int
    payment_date: datetime
