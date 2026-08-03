from pydantic import BaseModel, ConfigDict

class SaleItemBase(BaseModel):
    sale_id: int
    product_id: int
    quantity: int
    unit_price: float
    subtotal: float

class SaleItemCreate(SaleItemBase):
    pass

class SaleItemUpdate(BaseModel):
    quantity: int | None = None
    unit_price: float | None = None
    subtotal: float | None = None

class SaleItemResponse(SaleItemBase):
    sale_item_id: int
    model_config = ConfigDict(
        from_attributes=True
    )