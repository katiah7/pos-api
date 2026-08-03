from datetime import datetime
from pydantic import BaseModel, ConfigDict

class SaleBase(BaseModel):
    customer_id: int
    user_id: int
    sale_date: datetime
    total_amount: float
    payment_status: str

class SaleCreate(SaleBase):
    pass

class SaleUpdate(BaseModel):
    customer_id: int | None = None
    user_id: int | None = None
    sale_date: datetime | None = None
    total_amount: float | None = None
    payment_status: str | None = None

class SaleResponse(SaleBase):
    sale_id: int

    model_config = ConfigDict(
        from_attributes=True
    )