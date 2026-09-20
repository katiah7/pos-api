from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from schemas.common import Money


class ProductBase(BaseModel):
    product_name: str
    category_id: int
    supplier_id: int
    brand: str
    size: str | None = None
    color: str | None = None
    price: Money
    stock_quantity: int = Field(default=0, ge=0)
    barcode: str | None = None
    is_active: bool = True


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    product_name: str | None = None
    category_id: int | None = None
    supplier_id: int | None = None
    brand: str | None = None
    size: str | None = None
    color: str | None = None
    price: Money | None = None
    stock_quantity: int | None = Field(default=None, ge=0)
    barcode: str | None = None
    is_active: bool | None = None


class ProductRead(ProductBase):
    model_config = ConfigDict(from_attributes=True)

    product_id: int
    created_at: datetime
