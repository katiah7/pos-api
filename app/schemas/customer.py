from pydantic import BaseModel, ConfigDict
class CustomerBase(BaseModel):
    first_name: str
    last_name: str
    phone: str
    email: str
    loyalty_points: int = 0

class CustomerCreate(CustomerBase):
    pass

class CustomerUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    phone: str | None = None
    email: str | None = None
    loyalty_points: int | None = None

class CustomerResponse(CustomerBase):
    customer_id: int

    model_config = ConfigDict(
        from_attributes=True
    )