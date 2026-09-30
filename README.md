# Ivy League Learning

Free, interactive, Ivy-style learning platform: adaptive curriculum,
in-browser coding, full-stack studio, open-course library, community.

## Packages

| Path | What | Docs |
|---|---|---|
| `backend/` | FastAPI API (SQLite locally, Postgres via compose) | `backend/README.md` |
| `frontend/` | React + Vite SPA | `frontend/README.md` |
| `rust-core/` | Learning-math crate | `rust-core/README.md` |
| `Interactive Tool/` | Zero-install single-file demos | `Interactive Tool/README.md` |
| `docs/` | Setup + architecture + lab authoring | `docs/setup.md`, `docs/architecture.md`, `docs/labs.md` |

## Quickstart

```powershell
docker compose up --build   # Postgres + API on :8000
```

Local dev and per-package commands: [`docs/setup.md`](docs/setup.md).

## CI

`.github/workflows/ci.yml` runs backend (pytest + ruff), frontend
(`npm ci` + build), and Rust (test + clippy + fmt) on push/PR.
Note: the workflow is committed but Actions can't run while the
account has a billing lock — rerun once resolved.
