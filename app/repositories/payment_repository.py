from models.payment import Payment
from repositories.base import BaseRepository


class PaymentRepository(BaseRepository[Payment]):
    def __init__(self):
        super().__init__(Payment)


payment_repository = PaymentRepository()
