# Backend

The backend uses FastAPI, Poetry and Python 3.10 or later.

## First-time setup

These commands are for Windows Command Prompt. From the repository root:

```cmd
cd backend
python3 -m pip install --upgrade pip
python -m venv .venv
.venv\Scripts\activate
pip install poetry
```

After `pyproject.toml` has been created, install the project dependencies:

```cmd
poetry install
```

## Environment variables

The database settings are read from environment variables. Copy the example file and adjust the values if your local database differs:

```cmd
copy .env.example .env
```

The defaults match the PostgreSQL container in `db_scripts/docker-compose.yml`. `POSTGRES_USER` and `POSTGRES_PASSWORD` are required and the application will refuse to start without them.

| Variable | Default | Purpose |
|----------|---------|---------|
| `POSTGRES_HOST` | `localhost` | Database host |
| `POSTGRES_PORT` | `5432` | Database port |
| `POSTGRES_USER` | none | Database user |
| `POSTGRES_PASSWORD` | none | Database password |
| `POSTGRES_DB` | `waste_app` | Application database |
| `POSTGRES_MAINTENANCE_DB` | `postgres` | Used only to create the application database when it is missing |
| `POSTGRES_CONNECT_TIMEOUT` | `10` | Seconds to wait for a connection before failing |
| `JWT_SECRET_KEY` | none | Signs access tokens. At least 32 characters, and never shared between environments |
| `JWT_ALGORITHM` | `HS256` | Signing algorithm for access tokens |
| `JWT_EXPIRE_MINUTES` | `30` | How long an access token stays valid |

`JWT_SECRET_KEY` is required and has no default. Generate one with:

```cmd
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Anyone holding this value can mint a token for any user, so treat it exactly like a password. Changing it signs every existing token out.

## Database startup

The application prepares its database on startup. If the configured database does not exist it is created, and any outstanding Alembic migrations are applied. A database that already contains the tables but has never been managed by Alembic is adopted as it stands, without its data being touched.

Schema changes are made by adding an Alembic migration, never with `Base.metadata.create_all()`:

```cmd
poetry run alembic revision --autogenerate -m "describe the change"
poetry run alembic upgrade head
```

`.env` is ignored by Git and must never be committed.

## Authentication

M1 uses a **bearer token**, not a cookie. Clients send the token from sign-in on every later request:

```
Authorization: Bearer <access_token>
```

A secure `httpOnly` cookie is the stronger production choice, because JavaScript cannot read it and so an XSS bug cannot steal the session. It was not chosen for M1 because the frontend runs on a different origin from the API in development, and a cross-origin cookie requires `SameSite=None; Secure`, which requires HTTPS. Revisit this before any deployment.

| Method | Path | Auth | Purpose |
|--------|------|------|---------|
| `POST` | `/auth/register` | none | Create an account. `201` with the new user, `409` if the email is taken |
| `POST` | `/auth/login` | none | Exchange email and password for a token. `401` on failure |
| `POST` | `/auth/logout` | bearer | `204`. See the limitation below |
| `GET` | `/users/me` | bearer | The signed-in user. `401` if the token is missing or invalid |

Passwords are hashed with bcrypt and never stored or returned. Email addresses are lowercased before storage, so `Zahra@Example.com` and `zahra@example.com` are the same account. A failed sign-in returns the same response whether the email is unknown or the password is wrong.

### Admin access

Every user has a `role` column, `user` by default. There is no API to set it, and `role` in a registration or profile request body is ignored. To create the first admin, register a normal account through `/auth/register`, then promote it directly in the database:

```sql
UPDATE users SET role = 'admin' WHERE email = 'name@example.com';
```

Every admin route requires a bearer token for a user whose `role` is `admin`; anyone else gets `403`. A deactivated user's own token stops working everywhere, not just on admin routes, since `is_active` is checked in the same place the token itself is validated.

Bins and disposal instructions also carry `is_active`. A deactivated bin drops out of `GET /predictions/bins`, so users can no longer select it. Classification and bin-verification guidance are not filtered by `is_active` — instead, a bin cannot be deactivated at all while it is still the primary bin for a category, so that inconsistent state can't be created in the first place.

| Method | Path | Auth | Purpose |
|--------|------|------|---------|
| `GET` | `/admin/bins` | admin | List every bin, active or not |
| `POST` | `/admin/bins` | admin | Create a bin. `409` if the name is taken |
| `PATCH` | `/admin/bins/{id}` | admin | Update any of `name`, `colour`, `description`. `404`/`409` as above |
| `POST` | `/admin/bins/{id}/deactivate` | admin | Hide the bin from `/predictions/bins`. `404` if missing, `409` if it is a category's primary bin |
| `POST` | `/admin/bins/{id}/reactivate` | admin | Undo a deactivation. `404` if missing |
| `DELETE` | `/admin/bins/{id}` | admin | Hard delete. `409` if referenced by a mapping, prediction, or bin examination — deactivate it instead |
| `GET` | `/admin/disposal-instructions` | admin | List every instruction, active or not |
| `POST` | `/admin/disposal-instructions` | admin | Create an instruction for a category. `400` if the category does not exist |
| `PATCH` | `/admin/disposal-instructions/{id}` | admin | Update `instructions`/`notes`. `404` if missing |
| `POST` | `/admin/disposal-instructions/{id}/deactivate` | admin | `404` if missing |
| `POST` | `/admin/disposal-instructions/{id}/reactivate` | admin | `404` if missing |
| `GET` | `/admin/categories` | admin | List categories, read-only — there is no create/update/delete |
| `GET` | `/admin/category-bins` | admin | List every category↔bin mapping |
| `POST` | `/admin/category-bins` | admin | Connect a category to a bin. `400` if either does not exist, `409` on a duplicate pair or a second primary bin for the same category |
| `PATCH` | `/admin/category-bins/{id}` | admin | Set `is_primary`. `404`/`409` as above |
| `DELETE` | `/admin/category-bins/{id}` | admin | Disconnect a category from a bin. `404` if missing |

Only one mapping per category can be primary at a time, and the API rejects a second one rather than silently swapping it — to change which bin is primary for a category, unset the old mapping first (`PATCH` its `is_primary` to `false`), then set the new one.

| Method | Path | Auth | Purpose |
|--------|------|------|---------|
| `GET` | `/admin/users` | admin | List every user |
| `GET` | `/admin/users/{id}` | admin | View one user. `404` if it does not exist |
| `GET` | `/admin/users/{id}/predictions` | admin | That user's prediction history. `404` if the user does not exist |
| `POST` | `/admin/users/{id}/deactivate` | admin | Block that user's token from authenticating. `404` if the user does not exist |
| `POST` | `/admin/users/{id}/reactivate` | admin | Undo a deactivation. `404` if the user does not exist |

### Known limitations

- **Sign-out is client-side.** The token is not revoked, so it keeps working until it expires. `JWT_EXPIRE_MINUTES` is therefore the longest a signed-out token can still be used. Real revocation needs a stored denylist.
- **No refresh tokens.** Users sign in again when the token expires.
- **No rate limiting.** Sign-in attempts are unlimited, and each one costs a deliberate bcrypt delay.
- **Registration reveals whether an email is in use**, through the `409`, which sign-in deliberately does not.

## Classification

The backend loads four approved models (MobileNetV2, EfficientNet-B0, ResNet50, and DenseNet121). Each returns a probability distribution over the same 30 labels. The backend averages the probability vectors and chooses the class with the highest average probability. If one model fails to load, inference continues with the remaining models. If all models fail, the classification endpoint returns 503..

| Method | Path | Auth | Purpose |
|--------|------|------|---------|
| `POST` | `/predictions/` | bearer | Classify a JPEG or PNG image and return the disposal guidance for it |
| `GET` | `/predictions/history` | bearer | Return the signed-in user's predictions, newest first |

| Status | Meaning |
|--------|---------|
| `201` | Classified. The prediction is stored against the signed-in user |
| `400` | The image is empty or cannot be decoded |
| `413` | The image is larger than 5 MB |
| `415` | The type is not JPEG or PNG, or the content does not match the declared type |
| `503` | The model failed, or returned a result outside its contract |

Every prediction is checked before the database is consulted: the label index must exist in the label list, the label must be the one that index maps to, and the confidence must be a value between 0 and 1. Anything else is reported as `503` and nothing is stored. Without those checks a bad prediction surfaces later as a `500` that appears to blame the guidance data for a model problem.

### Known limitations

- **No low-confidence handling.** A weak prediction is returned like any other. The `confidence` value is part of the response, so a client can warn the user; agreeing a threshold with the ML team is milestone 3 work.
- **Four-model probability ensemble, CPU inference.**

## Run the tests

Run this command from `backend/`:

```cmd
python -m pytest
```

## Returning to the project

```cmd
cd backend
.venv\Scripts\activate
```

## Start the development server

Start PostgreSQL first from the repository root:

```cmd
docker compose -f db_scripts/docker-compose.yml up -d
```

Then run this command from `backend/`:

```cmd
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

The development server starts at <http://127.0.0.1:8000>. Use Uvicorn directly
because it avoids a Windows console Unicode error that can prevent `fastapi dev`
from starting.
