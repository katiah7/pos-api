# POS API

A REST API for a sports-merchandise point-of-sale system, built with **FastAPI**, **SQLAlchemy**, and **Pydantic**. It exposes authenticated endpoints for managing products, inventory records, customers, suppliers, sales, sale items, payments, receipts, and staff accounts.


## Contents

- [Overview](#overview)
- [Features](#features)
- [Technology stack](#technology-stack)
- [Architecture](#architecture)
- [Project structure](#project-structure)
- [API reference](#api-reference)
- [Authentication and authorization](#authentication-and-authorization)
- [Configuration](#configuration)
- [Local development](#local-development)
- [Testing](#testing)
- [Database behavior](#database-behavior)
- [Known limitations and setup issues](#known-limitations-and-setup-issues)
- [Contributing](#contributing)
- [License](#license)

## Overview

The POS API provides the backend services for a sports-merchandise point-of-sale workflow. It models the core records needed to manage a shop: a product catalogue linked to categories and suppliers, customers, staff users, sales and their line items, payment records, and receipts.

The application is organized into routers, Pydantic schemas, services, repositories, and SQLAlchemy models. API requests are validated by Pydantic schemas, processed by service functions, and persisted through repository classes using SQLAlchemy sessions.

The repository contains the API backend only. No frontend application, payment-provider integration, or deployed hosting configuration is included in the inspected source tree.

## Features

- **Product catalogue:** create, retrieve, update, and delete products, including brand, size, colour, price, stock quantity, barcode, category, supplier, and active status.
- **Category and supplier records:** maintain product categories and supplier contact details.
- **Customer records:** manage customer contact information and loyalty-point balances.
- **Sales:** create and manage sales associated with a customer and the staff user handling the sale.
- **Sale items:** record products and quantities against a sale; calculate line subtotals from quantity and unit price. If `unit_price` is omitted on creation, the service uses the current product price.
- **Payment records:** store a payment method, amount, transaction reference, and payment date against a sale.
- **Receipts:** store receipt numbers, issue dates, and totals associated with sales.
- **Staff accounts and roles:** support `admin` and `cashier` user roles, with administrator-only user management.
- **Authentication:** issue signed JWT access tokens after validating user credentials; reject inactive accounts and invalid or expired tokens.
- **Input validation and database conflict handling:** use Pydantic request/response schemas and return HTTP `409` for database integrity conflicts.
- **Automated tests:** provide pytest tests using an isolated in-memory SQLite database, plus a GitHub Actions workflow definition.

## Technology stack

| Area | Technology | Purpose |
|---|---|---|
| API framework | FastAPI | HTTP routing, dependency injection, and OpenAPI documentation |
| Data validation | Pydantic 2, pydantic-settings | Request/response schemas and settings management |
| ORM | SQLAlchemy 2 | Relational models, sessions, and persistence |
| Database driver | psycopg2-binary | PostgreSQL connectivity |
| Authentication | PyJWT | JWT access-token creation and validation |
| Password hashing | pwdlib with Argon2 | Password hashing and verification |
| ASGI server | Uvicorn | Local ASGI application server |
| Testing | pytest, FastAPI TestClient, HTTPX | API and service behavior tests |
| CI definition | GitHub Actions | Workflow configured to run pytest on pushes and pull requests |

## Architecture

The codebase uses a layered structure. Routers define HTTP endpoints and dependencies; schemas validate incoming and outgoing data; services contain resource-specific application logic; repositories perform common SQLAlchemy CRUD operations; and models define the database tables and relationships.

```mermaid
flowchart TD
    Client[API client] --> API[FastAPI application]
    API --> Auth[Authentication and authorization dependencies]
    API --> Routers[Resource routers]
    Routers --> Schemas[Pydantic schemas]
    Routers --> Services[Service layer]
    Services --> Repositories[Repository layer]
    Repositories --> ORM[SQLAlchemy models and sessions]
    ORM --> DB[(Relational database)]
```

The application registers the resource routers in `main.py`. On application startup, its lifespan handler calls `Base.metadata.create_all()` to create any missing tables. This is a simple schema-creation approach; no migration framework or migration history is present in the repository.

## Project structure

The uploaded archive contains the application files under `app/`:

```text
app/
├── .github/
│   └── workflows/
│       └── tests.yml          # GitHub Actions test workflow definition
├── core/
│   ├── config.py              # Application settings
│   ├── dependencies.py        # Current-user and admin dependencies
│   └── security.py            # Password hashing and JWT helpers
├── models/                    # SQLAlchemy table models and relationships
├── repositories/              # Shared and resource-specific database access
├── routers/                   # FastAPI route definitions
├── schemas/                   # Pydantic request and response schemas
├── services/                  # Resource and authentication logic
├── tests/                     # pytest suite, fixtures, and factories
├── create_admin.py            # Intended interactive admin bootstrap script
├── database.py                # SQLAlchemy engine, session factory, Base
├── main.py                    # FastAPI application and router registration
├── pytest.ini                 # pytest configuration
└── requirements.txt           # Pinned Python dependencies
```

## API reference

When the application is running locally, FastAPI exposes:

| Resource | URL | Description |
|---|---|---|
| Interactive API docs | `/docs` | Swagger UI |
| Alternative API docs | `/redoc` | ReDoc UI |
| OpenAPI schema | `/openapi.json` | Machine-readable API schema |
| Authentication | `/auth` | Login and current-user endpoint |
| Categories | `/categories` | Product categories |
| Suppliers | `/suppliers` | Supplier records |
| Products | `/products` | Product catalogue and stock fields |
| Customers | `/customers` | Customer records |
| Users | `/users` | Staff account management (admin only) |
| Sales | `/sales` | Sales records |
| Sale items | `/sale-items` | Items associated with sales |
| Payments | `/payments` | Payment records |
| Receipts | `/receipts` | Receipt records |

### Resource operations

Each resource router listed above, except `/auth`, implements the following operations:

| Method | Path pattern | Behavior | Success response |
|---|---|---|---|
| `GET` | `/{resource}/` | List records | `200 OK` |
| `GET` | `/{resource}/{id}` | Retrieve one record | `200 OK` |
| `POST` | `/{resource}/` | Create a record | `201 Created` |
| `PUT` | `/{resource}/{id}` | Update a record | `200 OK` |
| `DELETE` | `/{resource}/{id}` | Delete a record | `204 No Content` |

The concrete identifier names differ by resource (for example, `product_id`, `sale_id`, and `customer_id`). Refer to the generated OpenAPI schema for request and response fields.

### Authentication endpoints

| Method | Path | Description | Authentication |
|---|---|---|---|
| `POST` | `/auth/login` | Validate form-encoded username/password and return a bearer token | Public |
| `GET` | `/auth/me` | Return the authenticated user's public profile | Bearer token |

The login endpoint uses OAuth2 password-form fields (`username` and `password`), not a JSON login body.

## Authentication and authorization

Protected endpoints use the `Authorization: Bearer <access_token>` header. Tokens are signed JWTs and include the user ID as the subject and an expiration claim. The default token lifetime is 15 minutes.

Passwords are hashed using `pwdlib`'s recommended password-hashing configuration, which the test suite verifies produces Argon2id hashes. Inactive users cannot log in or continue using an otherwise valid token.

| Role | Access |
|---|---|
| `admin` | Can access all protected resource endpoints, including user management |
| `cashier` | Can access the shop resource endpoints; cannot access `/users` |

All resource routers require an authenticated user. The `/users` router additionally requires the `admin` role.

Example login request:

```bash
curl -X POST "http://127.0.0.1:8000/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  --data-urlencode "username=YOUR_USERNAME" \
  --data-urlencode "password=YOUR_PASSWORD"
```

Use the returned `access_token` in subsequent requests:

```bash
curl "http://127.0.0.1:8000/products/" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## Configuration

The application requires `DATABASE_URL` and `SECRET_KEY`. The settings class also supports the optional JWT settings below.

Create a `.env` file in the application directory (`app/.env` in the uploaded archive). The repository does not currently include a `.env.example` file.

| Variable | Required | Default | Description | Example |
|---|---|---|---|---|
| `DATABASE_URL` | Yes | — | SQLAlchemy database connection URL | `postgresql://USER:PASSWORD@localhost:5432/pos_db` |
| `SECRET_KEY` | Yes | — | Secret used to sign JWT access tokens | Generate a long, random value; do not commit it |
| `JWT_ALGORITHM` | No | `HS256` | JWT signing algorithm | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | No | `15` | Access-token lifetime in minutes | `30` |

Example `.env` template (replace the placeholders with local values):

```dotenv
DATABASE_URL=postgresql://YOUR_DB_USER:YOUR_DB_PASSWORD@localhost:5432/pos_db
SECRET_KEY=REPLACE_WITH_A_LONG_RANDOM_SECRET
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
```

The `.gitignore` excludes `.env`; keep real credentials and database passwords out of source control. The database module also calls `load_dotenv()` relative to the process working directory, so ensure `DATABASE_URL` is present in the process environment when launching the application.

## Local development

### Prerequisites

- Python 3.12 (the checked-in GitHub Actions workflow selects Python 3.12).
- PostgreSQL and a database/user for local development.
- Git.

### Install dependencies

The dependency file is located at `app/requirements.txt` in the uploaded archive. From the directory containing the `app/` folder:

```bash
python -m venv .venv
source .venv/bin/activate  # Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r app/requirements.txt
```

Create `app/.env` using the template in [Configuration](#configuration), then export its values before starting the server. For a POSIX shell, from the directory containing `app/`:

```bash
set -a
. app/.env
set +a
```

### Start the API

The source currently mixes package-qualified imports such as `app.database` with top-level imports such as `models` and `routers`. The following invocation supplies both import roots for the archive layout (`app/` as the source directory):

```bash
PYTHONPATH=".:./app" uvicorn app.main:app --reload
```

If your checkout has a different directory layout, resolve the import-path inconsistency described under [Known limitations and setup issues](#known-limitations-and-setup-issues) before relying on this command.

Once the server starts, open:

- Swagger UI: <http://127.0.0.1:8000/docs>
- ReDoc: <http://127.0.0.1:8000/redoc>

The application creates missing database tables at startup through SQLAlchemy `create_all()`. It does not run database migrations.

## Testing

The test suite is written with pytest and FastAPI's `TestClient`. Its fixtures configure a SQLite in-memory database, enable SQLite foreign-key enforcement, create a fresh schema for each test fixture, and override the application's database dependency. The tests cover authentication, authorization, configuration, password/JWT behavior, and the resource endpoints.

The checked-in workflow installs `app/requirements.txt` and runs `pytest` using Python 3.12. It is located at `.github/workflows/tests.yml` relative to the `app/` directory in the uploaded archive.

From the application repository root (the directory containing `tests/` and `pytest.ini`), the intended test command is:

```bash
pytest
```

Useful selections:

```bash
pytest -v
pytest tests/test_products.py
pytest -k "sale"
```

**Validation note:** The test suite was inspected, but a successful test run could not be confirmed in this audit environment because the installed runtime did not contain all project dependencies. The source-layout/import issue described below should also be resolved and the workflow run in the actual GitHub repository before treating CI as verified.

## Database behavior

- SQLAlchemy models define categories, suppliers, customers, users, products, sales, sale items, payments, and receipts.
- The database session is provided to request handlers through FastAPI dependency injection.
- Tables are created on application startup with `Base.metadata.create_all()`.
- Database integrity errors are converted to HTTP `409 Conflict` responses with a generic detail message.
- No Alembic configuration, migration scripts, seed dataset, or database backup procedure is present in the inspected repository.

## Known limitations and setup issues

The following items were identified during repository inspection. They are documented rather than silently worked around because this README task does not modify application code.

1. **Inconsistent Python import layout.** Modules import the database as `app.database` while also importing packages such as `models`, `routers`, and `services` as top-level modules. The correct import path depends on the checkout layout and working directory. Standard installation/startup commands should be verified after the package structure is made consistent.
2. **Admin bootstrap script is currently broken.** `create_admin.py` imports `session` from `app.database`, but `database.py` defines `SessionLocal` and does not define `session`. The documented script therefore cannot be relied on to create the first administrator until this mismatch is fixed.
3. **Missing environment example.** The tests expect an `.env.example` file, but no such file is present in the uploaded repository. Create `.env` manually using the template above; consider adding a safe `.env.example` in a future code change.
4. **CI workflow location depends on repository root.** The workflow is stored under `app/.github/workflows/tests.yml` in the uploaded archive. GitHub Actions only discovers workflows under `.github/workflows` at the repository root. Confirm the actual repository root and move the workflow if `app/` is a subdirectory in GitHub.
5. **No database migrations.** `create_all()` creates missing tables but does not provide a versioned schema migration path for existing deployments.
6. **No pagination is implemented in list endpoints.** Repository list methods currently return all records, which may not scale for large datasets.
7. **No payment-provider integration is present.** The payment model accepts method labels including `cash`, `mpesa`, `card`, and `crypto`; this is payment-record management, not evidence of a live payment gateway or M-Pesa API integration.
8. **No production deployment configuration is included.** The repository does not contain a Dockerfile, Compose configuration, hosting manifest, or documented production server setup.
9. **No project license is included.** See [License](#license).

## Contributing

Contributions should keep the existing separation of concerns and include tests for changed behavior.

1. Create a focused branch for the change.
2. Keep HTTP concerns in routers, validation in schemas, application logic in services, and database access in repositories.
3. Add or update pytest coverage for new behavior and regression cases.
4. Run the relevant tests and the full test suite before opening a pull request.
5. Describe the change, its impact, and any configuration or schema implications in the pull request.

No formal branch naming convention, formatter, linter, or pull-request template is defined in the repository.

## License

No `LICENSE` file or license declaration was present in the inspected repository. Unless the project owner adds a license, reuse, redistribution, and contribution terms are not explicitly granted. Add a license file before presenting the project as an open-source project.
