# Scoop Shop

Scoop Shop is a full-stack ice cream ordering application built with FastAPI,
PostgreSQL, SQLAlchemy, React, and TypeScript. Customers can browse flavors,
manage a cart, place orders, and review order history. Administrators can create,
edit, hide, and delete flavors.

## Features

- Account registration and JWT authentication
- Role-based customer and administrator authorization
- Paginated flavor browsing
- Cart add, quantity update, removal, and checkout
- Historical order snapshots that preserve purchased names and prices
- Paginated order history with expandable details
- Administrator flavor management
- Request validation, database constraints, and rate limiting
- Backend and frontend automated tests
- GitHub Actions checks for both applications

## Technology

### Backend

- FastAPI
- SQLAlchemy and PostgreSQL
- Alembic database migrations
- Pydantic request and response models
- PyJWT and Argon2 password hashing
- pytest
- uv for Python dependency management

### Frontend

- React and TypeScript
- Vite
- React Router
- React Context for authentication and cart state
- Vitest and React Testing Library
- ESLint
- npm for JavaScript dependency management

## Repository structure

```text
scoop-shop/
├── backend/                 FastAPI application and business logic
│   ├── routers/             API route modules
│   ├── auth.py              Password hashing and JWT creation
│   ├── config.py            Environment configuration
│   ├── database.py          SQLAlchemy engine and sessions
│   ├── models.py            Database models
│   └── schemas.py           Pydantic API schemas
├── migrations/              Alembic migration history
├── tests/                   Backend and integration tests
├── frontend/
│   ├── src/api.ts           Backend request functions
│   ├── src/auth/            Shared authentication state
│   ├── src/cart/            Shared cart state
│   ├── src/components/      Reusable UI components
│   └── src/pages/           Routed application pages
├── .github/workflows/       Continuous integration configuration
├── pyproject.toml           Python project and dependency configuration
└── uv.lock                  Reproducible Python dependency lockfile
```

## Prerequisites

- PostgreSQL
- Python 3.9 or newer
- [uv](https://docs.astral.sh/uv/)
- Node.js 22 or newer
- npm

## Local setup

### 1. Clone and enter the repository

```bash
git clone <repository-url>
cd scoop-shop
```

### 2. Create PostgreSQL databases

The application and tests use separate databases. Example commands are:

```bash
createdb scoop_shop
createdb scoop_shop_test
```

Database creation may differ depending on your PostgreSQL installation and user.

### 3. Configure the backend

```bash
cp .env.example .env
```

Update `.env` for your system:

```dotenv
JWT_SECRET_KEY=replace-with-a-long-random-secret
DATABASE_URL=postgresql+psycopg://username@localhost:5432/scoop_shop
TEST_DATABASE_URL=postgresql+psycopg://username@localhost:5432/scoop_shop_test
CORS_ORIGINS=http://localhost:5173
```

Generate a strong local JWT secret with `openssl rand -hex 32`. Never commit
`.env`; it contains machine-specific configuration and secrets.

### 4. Install backend dependencies and migrate the database

```bash
uv sync --locked --dev
uv run alembic upgrade head
```

Alembic creates and updates the database schema from the migration history.

### 5. Configure and install the frontend

```bash
cp frontend/.env.example frontend/.env
cd frontend
npm install
cd ..
```

The frontend environment file should contain:

```dotenv
VITE_API_URL=http://localhost:8000
```

Variables beginning with `VITE_` are exposed to browser code. Do not put secrets
in them.

## Running the application

Start the backend from the repository root:

```bash
uv run uvicorn backend.main:app --reload
```

The API is available at <http://localhost:8000>. Interactive API documentation
is available at <http://localhost:8000/docs>.

In a second terminal, start the frontend:

```bash
cd frontend
npm run dev
```

The application is available at <http://localhost:5173>.

## Creating an administrator

Administrator accounts are created or promoted through the backend CLI rather
than through a public API endpoint:

```bash
uv run python -m backend.create_admin admin@example.com
```

The command securely prompts for a password when creating a new account. If the
email already belongs to a customer, it asks whether to promote that account.

## Testing

Backend tests use `TEST_DATABASE_URL`. For safety, the database name must end in
`_test`. The test setup rebuilds the public schema, so never point it at a
development or production database.

```bash
uv run pytest
```

Run frontend checks from `frontend/`:

```bash
npm test
npm run lint
npm run build
```

`npm test` runs component tests once. `npm run build` also performs TypeScript
type checking before producing the optimized frontend bundle.

## Database migrations

After intentionally changing a SQLAlchemy model, generate and inspect a migration:

```bash
uv run alembic revision --autogenerate -m "describe the schema change"
uv run alembic upgrade head
```

Always review autogenerated migration files. Alembic detects structural changes,
but it cannot always infer the intended data migration or constraint behavior.

Useful commands:

```bash
uv run alembic current
uv run alembic history
uv run alembic downgrade -1
```

## API overview

| Area | Endpoints |
| --- | --- |
| Health | `GET /api/health` |
| Authentication | `POST /api/auth/register`, `POST /api/auth/login`, `GET /api/me` |
| Flavors | `GET /api/flavors`, `GET /api/flavors/{id}` |
| Admin flavors | `GET /api/flavors/manage`, `POST /api/flavors`, `PATCH /api/flavors/{id}`, `DELETE /api/flavors/{id}` |
| Cart | `GET /api/cart`, `POST /api/cart/items`, `PATCH /api/cart/items/{id}`, `DELETE /api/cart/items/{id}` |
| Orders | `POST /api/orders`, `GET /api/orders`, `GET /api/orders/{id}` |

Protected endpoints require this HTTP header:

```text
Authorization: Bearer <access-token>
```

The backend remains responsible for authorization. Frontend route guards improve
navigation but are not a security boundary.

## Continuous integration

The GitHub Actions workflow runs on pushes and pull requests. It starts an
isolated PostgreSQL service, runs all backend tests, and runs frontend linting,
tests, and the production build using locked dependencies.

## Production notes

Before deploying this project:

- Use a managed PostgreSQL database and a strong secret from a secret manager.
- Set `CORS_ORIGINS` to the deployed frontend origin.
- Set `VITE_API_URL` at frontend build time to the deployed API URL.
- Apply `alembic upgrade head` as part of the backend release process.
- Run the API behind HTTPS and a production process/container configuration.
- Replace the in-memory rate limiter with shared storage such as Redis when
  running multiple backend processes or servers.
- Configure the frontend host to serve `index.html` for unknown paths so React
  Router URLs work when refreshed directly.
