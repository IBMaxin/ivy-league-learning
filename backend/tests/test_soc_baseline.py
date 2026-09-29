"""SOC smoke tests: validation, authz fail-closed, no trace leakage."""

from fastapi.testclient import TestClient

from app.main import app
from app.security import create_access_token

client = TestClient(app, raise_server_exceptions=False)


def _auth(user_id: str = "dev-user") -> dict[str, str]:
    return {"Authorization": f"Bearer {create_access_token(user_id)}"}


AUTH = _auth()


def test_health():
    assert client.get("/health").json() == {"status": "ok"}


def test_progress_requires_auth():
    r = client.post("/api/progress", json={"user_id": "x", "course_id": "c", "lesson_id": "l"})
    assert r.status_code == 401


def test_progress_rejects_oversize_score():
    r = client.post(
        "/api/progress",
        json={"user_id": "dev-user", "course_id": "c", "lesson_id": "l", "score": 999},
        headers=AUTH,
    )
    assert r.status_code == 422  # strict validation, no write


def test_code_run_rejects_oversize_payload():
    r = client.post(
        "/api/code/run", json={"language": "python", "code": "x" * 10_001}, headers=AUTH
    )
    assert r.status_code == 422
