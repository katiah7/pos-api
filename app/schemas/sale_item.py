from pydantic import BaseModel, ConfigDict, Field

from schemas.common import Money


class SaleItemBase(BaseModel):
    sale_id: int
    product_id: int
    quantity: int = Field(gt=0)


class SaleItemCreate(SaleItemBase):
    unit_price: Money | None = None


class SaleItemUpdate(BaseModel):
    sale_id: int | None = None
    product_id: int | None = None
    quantity: int | None = Field(default=None, gt=0)
    unit_price: Money | None = None


class SaleItemRead(SaleItemBase):
    model_config = ConfigDict(from_attributes=True)

    sale_item_id: int
    unit_price: Money
    subtotal: Money
