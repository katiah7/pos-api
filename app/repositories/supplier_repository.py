from models.supplier import Supplier
from repositories.base import BaseRepository


class SupplierRepository(BaseRepository[Supplier]):
    def __init__(self):
        super().__init__(Supplier)


supplier_repository = SupplierRepository()
