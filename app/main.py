from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError

import models  # noqa: F401  (registers every table with Base before create_all)
from app.database import Base, engine
from routers import (
    auth,
    categories,
    customers,
    payments,
    products,
    receipts,
    sale_items,
    sales,
    suppliers,
    users,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables when the server starts (not when the module is imported,
    # so the tests can import `app` without a PostgreSQL server running).
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="POS API", version="1", lifespan=lifespan)


@app.exception_handler(IntegrityError)
def integrity_error_handler(request: Request, exc: IntegrityError):
    # Duplicate value, a foreign key pointing at a row that doesn't exist,
    # or deleting a row that other rows still reference.
    return JSONResponse(
        status_code=409,
        content={
            "detail": "Database constraint violated: duplicate value, "
            "missing related record, or record still in use."
        },
    )


app.include_router(auth.router)
app.include_router(categories.router)
app.include_router(suppliers.router)
app.include_router(products.router)
app.include_router(customers.router)
app.include_router(users.router)
app.include_router(sales.router)
app.include_router(sale_items.router)
app.include_router(payments.router)
app.include_router(receipts.router)
