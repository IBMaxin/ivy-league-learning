# Ivy Backend

FastAPI API for the learning platform. One concern per module.

## Layout

| Path | Concern |
|---|---|
| `app/main.py` | Wiring only: app, middleware, router mounting |
| `app/config.py` | Env-driven settings, no secrets in code |
| `app/security.py` | HS256 JWT verify + response headers |
| `app/routers/auth.py` | `POST /api/auth/token` mints JWT for a user_id |
| `app/store.py` — removed | SQLAlchemy via `db`/`tables`/`repos` (SQLite file locally, Postgres via `IVY_DATABASE_URL`) |
| `app/models.py` | Pydantic validation models |
| `app/db.py` | Engine + sessions + `init_db` (lifespan) |
| `app/tables.py` | ORM tables: `progress`, `posts` |
| `app/repos.py` | Data access: sessions in, plain data out |
| `app/services.py` | Pure learning logic: mastery, grading, recommendations |
| `app/content.py` | Static tracks, library links, quizzes |
| `app/routers/curriculum.py` | Public curriculum + library reads |
| `app/routers/progress.py` | Authed progress reads/writes |
| `app/routers/quiz.py` | Public quiz fetch, authed submit, adaptive |
| `app/routers/community.py` | Public post listing, authed creation |
| `app/routers/sandbox.py` | Code-run stub (never executes user code) + health |

## Commands (run in `backend/`)

```powershell
uv sync --extra dev --frozen
uv run --frozen pytest -q
uv run --frozen ruff check .
uv run --frozen uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Postgres via compose (run at repo root): `docker compose up --build`.
Tests use an isolated in-memory SQLite database (`tests/conftest.py`).

## Auth

```powershell
# Mint (dev-user must match ^[A-Za-z0-9_-]{1,64}$)
Invoke-RestMethod -Method Post -Uri http://localhost:8000/api/auth/token `
  -ContentType 'application/json' -Body '{"user_id":"dev-user"}'
```

Send `Authorization: Bearer <jwt>` on progress/quiz/community/sandbox calls.
Missing/garbage/expired token is 401; valid token for the wrong `user_id` is 403.
