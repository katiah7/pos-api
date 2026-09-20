# Importing every model here means Base.metadata knows about all the tables
# (and string-based relationship() targets can be resolved) as soon as
# anything in the `models` package is imported.
from models.category import Category
from models.supplier import Supplier
from models.customer import Customer
from models.user import User
from models.product import Product
from models.sale import Sale
from models.sale_item import SaleItem
from models.payment import Payment
from models.receipt import Receipt

__all__ = [
    "Category",
    "Supplier",
    "Customer",
    "User",
    "Product",
    "Sale",
    "SaleItem",
    "Payment",
    "Receipt",
]
