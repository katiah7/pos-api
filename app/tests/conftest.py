import os
import secrets

os.environ["DATABASE_URL"] = "sqlite://"
os.environ["SECRET_KEY"] = secrets.token_urlsafe(32)  
os.environ["JWT_ALGORITHM"] = "HS256"
os.environ["ACCESS_TOKEN_EXPIRE_MINUTES"] = "15"

import pytest  
from fastapi.testclient import TestClient
from pwdlib import PasswordHash
from pwdlib.hashers.argon2 import Argon2Hasher
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import app.database as database
import models 
from core import security
from core.security import hash_password
from app.database import Base, get_db
from app.main import app
from models.user import User
from tests.factories import (
    category_payload,
    customer_payload,
    product_payload,
    sale_payload,
    supplier_payload,
)

assert database.engine.url.get_backend_name() == "sqlite"

security.password_hasher = PasswordHash(
    (Argon2Hasher(time_cost=1, memory_cost=1024, parallelism=1),)
)

ADMIN_PASSWORD = "admin-pass-123"
CASHIER_PASSWORD = "cashier-pass-123"
ADMIN_HASH = hash_password(ADMIN_PASSWORD)
CASHIER_HASH = hash_password(CASHIER_PASSWORD)


@pytest.fixture
def session_factory():
    """A brand-new in-memory SQLite database for every test."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    @event.listens_for(engine, "connect")
    def _enable_foreign_keys(dbapi_connection, connection_record):
        dbapi_connection.execute("PRAGMA foreign_keys=ON")

    Base.metadata.create_all(bind=engine)
    yield sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture
def client(session_factory):
    def override_get_db():
        db = session_factory()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


def _add_user(session_factory, username, password_hash, role, full_name):
    with session_factory() as db:
        user = User(
            username=username,
            password_hash=password_hash,
            full_name=full_name,
            role=role,
            is_active=True,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return {"user_id": user.user_id, "username": user.username}


def _login(client, username, password):
    response = client.post(
        "/auth/login", data={"username": username, "password": password}
    )
    assert response.status_code == 200, response.text
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


@pytest.fixture
def admin_user(session_factory):
    return _add_user(session_factory, "admin", ADMIN_HASH, "admin", "Admin User")


@pytest.fixture
def auth_header(client, admin_user):
    """Authorization header of a logged-in admin."""
    return _login(client, "admin", ADMIN_PASSWORD)


@pytest.fixture
def cashier_header(client, session_factory):
    """Authorization header of a logged-in cashier (not an admin)."""
    _add_user(session_factory, "cashier", CASHIER_HASH, "cashier", "Cashier User")
    return _login(client, "cashier", CASHIER_PASSWORD)


def _create(client, url, header, payload):
    response = client.post(url, json=payload, headers=header)
    assert response.status_code == 201, response.text
    return response.json()


@pytest.fixture
def category(client, auth_header):
    return _create(client, "/categories/", auth_header, category_payload())


@pytest.fixture
def supplier(client, auth_header):
    return _create(client, "/suppliers/", auth_header, supplier_payload())


@pytest.fixture
def product(client, auth_header, category, supplier):
    payload = product_payload(category["category_id"], supplier["supplier_id"])
    return _create(client, "/products/", auth_header, payload)


@pytest.fixture
def customer(client, auth_header):
    return _create(client, "/customers/", auth_header, customer_payload())


@pytest.fixture
def sale(client, auth_header, customer, admin_user):
    payload = sale_payload(customer["customer_id"], admin_user["user_id"])
    return _create(client, "/sales/", auth_header, payload)
