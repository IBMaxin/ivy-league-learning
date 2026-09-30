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
| `routers/lab.py` | Lab HTTP only: serves `LABS` prompts, persists attempts via `repos` |
| `repos.py` | SQL only: sessions in, plain data out |
| `services.py` | Pure functions: mastery, grading, recommendations, lab scoring |
| `sandbox.py` | All code execution: allowlisted AST only — never `exec`/`eval`/import |
| `content.py` | Static tracks, library links, quizzes, lab fixtures (`LABS`) |
| `models.py` | Pydantic validation (`QuizSubmit`, `LabSubmit`, …) |
| `db.py` / `tables.py` | Engine, sessions, ORM tables |
| `config.py` / `security.py` | Settings, HS256 JWT verify (`iss`/`aud`/`exp`/`sub`) + headers |
| `routers/auth.py` | `POST /api/auth/token` mints JWT for a `user_id` |

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
| `mastery.rs` | Score averaging, quiz grading, pace, next-lesson pick |
| `validate.rs` | Submission validation |

Mirrors `services.py` logic (70% mastery threshold, quiz grading to 1 decimal,
pace cutoffs at 5/10 attempts); the two must agree.

## Data flow (quiz submit)

1. `POST /api/quiz/submit` validates shape (`models.py`) + caller (`security.py`)
2. `services.grade_quiz` scores against `content.QUIZZES`
3. `repos.add_progress` persists the attempt
4. `services.recommend_next` picks review vs. next lesson from stored mastery

## Data flow (lab submit)

1. `POST /api/lab/submit` validates shape (`models.LabSubmit`) + caller (`security.py`);
   `user_id` comes from the verified token, never the request body
2. `services.validate_lab` scores against `content.LABS` by delegating
   execution to `sandbox.run_lab` (allowlisted AST interpreter, never `exec`)
3. `repos.add_progress` persists the attempt with `score`/`completed`, so labs
   feed `mastery_of` / `recommend_next` / `Progress` exactly like quizzes

## Auth flow (JWT)

1. `POST /api/auth/token` with `{"user_id": "..."}` returns `{"access_token", "token_type": "bearer"}`
2. Client stores the token (`localStorage ivy-token`) and sends `Authorization: Bearer <jwt>`
3. `security.get_current_user_id` verifies HS256 signature + `iss`/`aud`/`exp`/`sub`, returns `sub`
4. Routers enforce ownership: `payload.user_id == caller`, else 403; missing/invalid token is 401
