# Sushi App

A mobile-first ordering application for Sushi Poços. The MVP will allow customers to browse the menu, configure products, manage a shopping cart, choose delivery or pickup, place orders and track their status. Restaurant staff will have a protected area for managing orders and menu availability.

## Project status

The project is in its MVP development phase. The backend exposes a health response plus database-backed category and product APIs. The customer interface and the remaining administrative features are tracked as separate GitHub issues.

The initial database schema and its first reversible Alembic migration are available. Public catalog endpoints only expose active products from active categories.

## Planned stack

- **Frontend:** Next.js, React and TypeScript
- **Backend:** Python and FastAPI
- **Database:** PostgreSQL with SQLAlchemy
- **Testing:** pytest and FastAPI TestClient
- **Version control:** Git and GitHub

The detailed technical boundaries and request flows are documented in [docs/architecture.md](docs/architecture.md).

## Repository structure

```text
sushi-app/
|-- backend/
|   |-- app/
|   |   |-- routes/
|   |   `-- main.py
|   |-- tests/
|   |-- .env.example
|   |-- requirements.txt
|   `-- requirements-dev.txt
|-- docs/
|   `-- architecture.md
|-- frontend/
|-- pytest.ini
`-- README.md
```

## Run the backend locally

### Requirements

- Python 3.13+
- Git

### Setup

```bash
python -m venv backend/.venv
```

Activate the virtual environment on Windows:

```powershell
backend\.venv\Scripts\Activate.ps1
```

Install the development dependencies:

```bash
python -m pip install -r backend/requirements-dev.txt
```

Create the local environment file:

```powershell
Copy-Item backend/.env.example backend/.env
```

Start the API from the repository root:

```bash
uvicorn app.main:app --app-dir backend --reload
```

Apply the database migrations from the repository root:

```bash
alembic -c backend/alembic.ini upgrade head
```

Roll back the latest migration:

```bash
alembic -c backend/alembic.ini downgrade -1
```

Useful local URLs:

- API root: `http://127.0.0.1:8000/`
- Products: `http://127.0.0.1:8000/products`
- Interactive API documentation: `http://127.0.0.1:8000/docs`

## Run the tests

```bash
python -m pytest
```

## Development workflow

Each change follows this workflow:

```text
Issue -> Branch -> Implementation -> Tests -> Commit -> Push -> Pull Request -> Review -> Merge
```

Branch names include the related issue number, for example:

```text
chore/2-project-foundation
feat/4-categories-api
```

## Current API endpoints

| Method | Endpoint | Description |
| --- | --- | --- |
| `GET` | `/` | Confirms that the API is running |
| `GET` | `/categories` | Lists active menu categories |
| `GET` | `/products` | Lists available products; accepts a `category` slug filter |
| `GET` | `/products/{id}` | Retrieves an available product |
| `POST` | `/admin/categories` | Creates a category |
| `PATCH` | `/admin/categories/{id}` | Renames a category |
| `DELETE` | `/admin/categories/{id}` | Deactivates a category |
| `POST` | `/admin/products` | Creates a product |
| `PATCH` | `/admin/products/{id}` | Updates product data and availability |

## Security

- Never commit `.env` files, passwords, tokens or database credentials.
- Keep only safe example values in `.env.example`.
- Category management currently requires the `X-Admin-Key` header configured through `ADMIN_API_KEY`.
- The development-only fallback key is rejected outside development and test environments.
- Token-based administrator authentication will replace this temporary key before publication.

## License

No license has been selected yet. All rights are reserved until a license is added.
