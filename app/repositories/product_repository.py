from models.product import Product
from repositories.base import BaseRepository


class ProductRepository(BaseRepository[Product]):
    def __init__(self):
        super().__init__(Product)


product_repository = ProductRepository()
