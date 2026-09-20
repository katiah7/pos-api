from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from repositories.sale_item_repository import sale_item_repository
from schemas.sale_item import SaleItemCreate, SaleItemUpdate
from services import product_service


def get_sale_item(db: Session, sale_item_id: int):
    sale_item = sale_item_repository.get(db, sale_item_id)
    if not sale_item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sale item not found")
    return sale_item


def list_sale_item(db: Session):
    return sale_item_repository.get_all(db)


def create_sale_item(db: Session, data: SaleItemCreate):
    values = data.model_dump()
    if values["unit_price"] is None:
        values["unit_price"] = product_service.get_product(db, values["product_id"]).price
    values["subtotal"] = values["unit_price"] * values["quantity"]
    return sale_item_repository.create(db, values)


def update_sale_item(db: Session, sale_item_id: int, data: SaleItemUpdate):
    sale_item = get_sale_item(db, sale_item_id)
    values = data.model_dump(exclude_unset=True)

    quantity = values.get("quantity")
    if quantity is None:
        quantity = sale_item.quantity
    unit_price = values.get("unit_price")
    if unit_price is None:
        unit_price = sale_item.unit_price
    values["quantity"] = quantity
    values["unit_price"] = unit_price
    values["subtotal"] = unit_price * quantity

    return sale_item_repository.update(db, sale_item, values)


def delete_sale_item(db: Session, sale_item_id: int):
    sale_item = get_sale_item(db, sale_item_id)
    sale_item_repository.delete(db, sale_item)
