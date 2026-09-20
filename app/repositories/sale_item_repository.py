from models.sale_item import SaleItem
from repositories.base import BaseRepository


class SaleItemRepository(BaseRepository[SaleItem]):
    def __init__(self):
        super().__init__(SaleItem)


sale_item_repository = SaleItemRepository()
