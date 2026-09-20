"""Small helpers that build valid request bodies. Pass keyword arguments to
override any field, e.g. product_payload(1, 1, price="10.00")."""


def category_payload(**overrides):
    return {"category_name": "Jerseys", "description": "Team and national jerseys", **overrides}


def supplier_payload(**overrides):
    return {
        "supplier_name": "Nike Kenya",
        "contact_person": "Amina Otieno",
        "phone": "+254700000001",
        "email": "orders@nikeke.co.ke",
        "address": "Industrial Area, Nairobi",
        **overrides,
    }


def product_payload(category_id, supplier_id, **overrides):
    return {
        "product_name": "Home Jersey",
        "category_id": category_id,
        "supplier_id": supplier_id,
        "brand": "Nike",
        "size": "L",
        "color": "Red",
        "price": "59.99",
        "stock_quantity": 10,
        "barcode": "6001234567890",
        **overrides,
    }


def customer_payload(**overrides):
    return {
        "first_name": "Brian",
        "last_name": "Mwangi",
        "phone": "+254711000002",
        "email": "brian@mailbox.co.ke",
        **overrides,
    }


def user_payload(**overrides):
    return {
        "username": "cashier1",
        "password": "cashier-pass-1",
        "full_name": "Cashier One",
        "role": "cashier",
        **overrides,
    }


def sale_payload(customer_id, user_id, **overrides):
    return {
        "customer_id": customer_id,
        "user_id": user_id,
        "total_amount": "119.98",
        **overrides,
    }


def sale_item_payload(sale_id, product_id, **overrides):
    return {"sale_id": sale_id, "product_id": product_id, "quantity": 2, **overrides}


def payment_payload(sale_id, **overrides):
    return {
        "sale_id": sale_id,
        "payment_method": "mpesa",
        "amount_paid": "119.98",
        "transaction_reference": "QGH7X2K9LM",
        **overrides,
    }


def receipt_payload(sale_id, **overrides):
    return {
        "sale_id": sale_id,
        "receipt_number": "RCPT-0001",
        "total_amount": "119.98",
        **overrides,
    }
