# Architecture

Separation of concerns: each module owns one layer.

## Backend (`backend/app/`)

```
HTTP (routers/) → data access (repos.py) → pure logic (services.py)
                          ↓
                    sessions (db.py) → tables (tables.py)
```

| Module | Owns |
|---|---|
| `main.py` | Wiring: app, middleware, lifespan, router mounting |
| `routers/*` | HTTP only: status codes, auth, input/output shape |
| `repos.py` | SQL only: sessions in, plain data out |
| `services.py` | Pure functions: mastery, grading, recommendations |
| `content.py` | Static tracks, library links, quizzes |
| `models.py` | Pydantic validation |
| `db.py` / `tables.py` | Engine, sessions, ORM tables |
| `config.py` / `security.py` | Settings, auth stub + headers |

Storage: SQLite file locally (`ivy.db`), Postgres via `IVY_DATABASE_URL`
(compose/prod). Tables auto-created on startup; welcome post seeded once.

## Frontend (`frontend/src/`)

| Path | Owns |
|---|---|
| `api/client.ts` | All HTTP, no UI |
| `api/runner.ts` | Local code execution/analysis, no network |
| `hooks/` | Remote data state |
| `components/` | Rendering only |
| `App.tsx` | View switching |

## Rust (`rust-core/src/`)

| Module | Owns |
|---|---|
| `lib.rs` | Re-exports |
| `mastery.rs` | Score averaging + next-lesson pick |
| `validate.rs` | Submission validation |

Mirrors `services.py` logic; the two must agree on the 70% mastery threshold.

## Data flow (quiz submit)

1. `POST /api/quiz/submit` validates shape (`models.py`) + caller (`security.py`)
2. `services.grade_quiz` scores against `content.QUIZZES`
3. `repos.add_progress` persists the attempt
4. `services.recommend_next` picks review vs. next lesson from stored mastery
