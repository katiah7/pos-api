from pydantic import BaseModel, ConfigDict, EmailStr


class SupplierBase(BaseModel):
    supplier_name: str
    contact_person: str
    phone: str
    email: EmailStr
    address: str


class SupplierCreate(SupplierBase):
    pass


class SupplierUpdate(BaseModel):
    supplier_name: str | None = None
    contact_person: str | None = None
    phone: str | None = None
    email: EmailStr | None = None
    address: str | None = None


class SupplierRead(SupplierBase):
    model_config = ConfigDict(from_attributes=True)

    supplier_id: int
