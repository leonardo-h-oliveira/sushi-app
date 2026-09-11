# Sushi App

A mobile-first ordering application for Sushi Poços. The MVP allows customers to browse the menu, configure products, manage a shopping cart, choose delivery or pickup, place orders and track their status. Restaurant staff have a protected area for managing orders and menu availability.

## Project status

The MVP is implemented and covered by automated backend and frontend checks. The backend exposes database-backed catalog, authentication, order and administration APIs. The frontend includes the customer menu, product details, cart, checkout, order tracking, staff order management and menu management screens.

The initial database schema and its reversible Alembic migrations are available. Public catalog endpoints only expose active products from active categories.

## Stack

- **Frontend:** Next.js, React, TypeScript and Tailwind CSS
- **Backend:** Python, FastAPI and SQLAlchemy
- **Database:** SQLite for local development; PostgreSQL-ready configuration
- **Migrations:** Alembic
- **Testing:** pytest, FastAPI TestClient and Vitest
- **Version control and CI:** Git, GitHub and GitHub Actions

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
|-- .github/workflows/ci.yml
|-- pytest.ini
`-- README.md
```

## Run the backend locally

### Requirements

- Python 3.13+
- Node.js 24+
- pnpm 10+
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

Populate the local database with the initial restaurant menu:

```powershell
python backend/seed.py
```

The seeder is idempotent: running it again updates the 17 categories and 10
products instead of creating duplicates.

Roll back the latest migration:

```bash
alembic -c backend/alembic.ini downgrade -1
```

Useful local URLs:

- API root: `http://127.0.0.1:8000/`
- Health probe: `http://127.0.0.1:8000/health`
- Products: `http://127.0.0.1:8000/products`
- Interactive API documentation: `http://127.0.0.1:8000/docs`

## Run the frontend locally

Install the frontend dependencies and create its local environment file:

```powershell
pnpm --dir frontend install
Copy-Item frontend/.env.local.example frontend/.env.local
```

Start the Next.js development server:

```powershell
pnpm --dir frontend dev
```

The customer menu is available at `http://localhost:3000`. Staff tools are available at `/admin/orders` and `/admin/menu`.

## Quality checks

Run the complete local validation suite:

```powershell
backend\.venv\Scripts\python -m pytest
pnpm --dir frontend exec vitest run
pnpm --dir frontend exec eslint .
pnpm --dir frontend exec next build
```

GitHub Actions runs the backend tests, frontend tests, ESLint and the production build for every pull request and every push to `main`.

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
| `GET` | `/health` | Returns a deployment health status |
| `GET` | `/categories` | Lists active menu categories |
| `GET` | `/products` | Lists available products; accepts a `category` slug filter |
| `GET` | `/products/{id}` | Retrieves an available product |
| `POST` | `/auth/login` | Authenticates a staff member |
| `POST` | `/auth/logout` | Validates a staff session logout request |
| `GET` | `/orders` | Lists orders for authenticated staff |
| `PATCH` | `/orders/{number}/status` | Updates an order status for authenticated staff |
| `POST` | `/admin/categories` | Creates a category |
| `PATCH` | `/admin/categories/{id}` | Renames or updates a category |
| `DELETE` | `/admin/categories/{id}` | Deactivates a category |
| `POST` | `/admin/products` | Creates a product |
| `PATCH` | `/admin/products/{id}` | Updates product data and availability |

## Security

- Never commit `.env` files, passwords, tokens or database credentials.
- Keep only safe example values in `.env.example`.
- Staff routes require signed bearer authentication configured through the administrator environment variables.
- The legacy `X-Admin-Key` mechanism remains available only for compatible development and test flows.

## License

No license has been selected yet. All rights are reserved until a license is added.
