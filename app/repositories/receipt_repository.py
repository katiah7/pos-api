from models.receipt import Receipt
from repositories.base import BaseRepository


class ReceiptRepository(BaseRepository[Receipt]):
    def __init__(self):
        super().__init__(Receipt)


receipt_repository = ReceiptRepository()
