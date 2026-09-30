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
| `app/models.py` | Pydantic validation models (`QuizSubmit`, `LabSubmit`, …) |
| `app/db.py` | Engine + sessions + `init_db` (lifespan) |
| `app/tables.py` | ORM tables: `progress`, `posts` |
| `app/repos.py` | Data access: sessions in, plain data out |
| `app/services.py` | Pure learning logic: mastery, grading, recommendations, lab scoring |
| `app/content.py` | Static tracks, library links, quizzes, lab fixtures (`LABS`) |
| `app/routers/curriculum.py` | Public curriculum + library reads |
| `app/routers/progress.py` | Authed progress reads/writes |
| `app/routers/quiz.py` | Public quiz fetch, authed submit, adaptive |
| `app/routers/community.py` | Public post listing, authed creation |
| `app/sandbox.py` | Safe preview: allowlisted Python AST, JS/Rust static analysis; `run_lab` interprets lab functions (never exec) |
| `app/routers/sandbox.py` | Authed `POST /api/code/run`, never exec/import in API process |
| `app/routers/lab.py` | Authed lab fetch + submit; persists attempts as progress for the token caller |

## Commands (run in `backend/`)

```powershell
uv sync --extra dev --frozen
uv run --frozen pytest -q
uv run --frozen ruff check .
uv run --frozen uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Postgres via compose (run at repo root): `docker compose up --build`.
Tests use an isolated in-memory SQLite database (`tests/conftest.py`).

## Sandbox (`POST /api/code/run`, auth required)

- Python: allowlisted AST only — `print()`, `x = ...`, `range()`, `for`/`while`/`if`
  (capped: 100 loop iters, 50 prints, 10k steps). No imports, no exec/eval/open.
- JavaScript: static preview of `console.log` calls — full run stays in the browser Coding Lab.
- Rust: static analysis (`fn main`, `unsafe`, `println!` count) — compile with `cargo run` locally.

## Labs (`GET /api/lab/{id}`, `POST /api/lab/submit`, auth required)

Server-graded function challenges. Submit `{"lesson_id", "code"}` (≤ 10k chars);
`user_id` is taken from the token. Returns `{success, score, correct, total,
results[]}` and records the attempt as progress. Full contract, safety model,
and authoring guide: [`docs/labs.md`](../docs/labs.md).

## Auth

```powershell
# Mint (dev-user must match ^[A-Za-z0-9_-]{1,64}$)
Invoke-RestMethod -Method Post -Uri http://localhost:8000/api/auth/token `
  -ContentType 'application/json' -Body '{"user_id":"dev-user"}'
```

Send `Authorization: Bearer <jwt>` on progress/quiz/community/sandbox calls.
Missing/garbage/expired token is 401; valid token for the wrong `user_id` is 403.
