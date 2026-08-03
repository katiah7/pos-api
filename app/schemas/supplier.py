from pydantic import BaseModel, ConfigDict

class SupplierBase(BaseModel):
    supplier_name: str
    contact_person: str
    phone: str
    email: str
    address: str

class SupplierCreate(SupplierBase):
    pass

class SupplierUpdate(BaseModel):
    supplier_name: str | None = None
    contact_person: str | None = None
    phone: str | None = None
    email: str | None = None
    address: str | None = None

class SupplierResponse(SupplierBase):
    supplier_id: int

    model_config = ConfigDict(
        from_attributes=True
    )