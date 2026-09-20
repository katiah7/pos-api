from models.sale import Sale
from repositories.base import BaseRepository


class SaleRepository(BaseRepository[Sale]):
    def __init__(self):
        super().__init__(Sale)


sale_repository = SaleRepository()
