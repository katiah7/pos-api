from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from models.product import Product
from repositories.product_repository import product_repository
from schemas.product import ProductCreate, ProductUpdate 

def get_product(db:Session, id:int):
    product = product_repository.get(db, id)
    if not product:
        raise HTTPException ( status=404, detail="product not found")
    return product

def list_product(db:Session):
    return product_repository.get_all(db)

def create_product(db: Session, data: ProductCreate):
    return product_repository.create(db, data.model_dump())

def update_product(db:Session, product_id:int, data: ProductUpdate):
    product = get_product(db, product_id)
    return product_repository.update(db, product, data.model_dump(exclude_unset=True))

def delete_product(db: Session, product_id: int):
    product = get_product(db, product_id)
    product_repository.delete(db, product)