# POS Backend

FastAPI backend for a sports-merchandise point-of-sale system: products,
categories, suppliers, customers, users, sales, sale items, payments and
receipts, with login (JWT) and admin / cashier roles.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate         
pip install -r requirements.txt
```

```bash
cp .env.example .env               
```
### Run the app

```bash
python create_admin.py            
uvicorn main:app --reload
```

Interactive API docs: http://localhost:8000/docs

## Running the tests

The tests use an in-memory **SQLite** database and their own throw-away
settings, so they never touch your PostgreSQL database and do not need a
`.env` file.

```bash
pip install -r requirements.txt    
pytest
```

Useful variations:

```bash
pytest -v                         
pytest tests/test_products.py     
pytest -k "sale"                  
```

Every test must pass (`0 failed`) before you push.

## Continuous integration

`.github/workflows/tests.yml` runs the full test suite with GitHub Actions on
every push and whenever a pull request is opened or updated. The workflow
fails if any test fails.

## Project layout

```
main.py            app entry point
database.py        engine and session
core/              settings (.env), security (argon2, JWT), auth dependencies
models/            SQLAlchemy tables
schemas/           Pydantic request / response models
repositories/      database access
services/          business logic
routers/           API endpoints
tests/             pytest suite (fixtures in conftest.py)
```
