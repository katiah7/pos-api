from datetime import datetime
from pydantic import BaseModel, ConfigDict

class PaymentBase(BaseModel):
    sale_id: int
    payment_method: str
    amount_paid: float
    payment_date: datetime
    transaction_reference: str

class PaymentCreate(PaymentBase):
    pass

class PaymentUpdate(BaseModel):
    payment_method: str | None = None
    amount_paid: float | None = None
    payment_date: datetime | None = None
    transaction_reference: str | None = None

class PaymentResponse(PaymentBase):
    payment_id: int

    model_config = ConfigDict(
        from_attributes=True
    )