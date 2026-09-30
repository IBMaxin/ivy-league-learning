"""Router layer tests: HTTP shape, auth, status codes only.

No execution logic asserted here beyond one happy-path roundtrip;
grading correctness lives in test_lab_sandbox.py / test_lab_services.py.
"""

from fastapi.testclient import TestClient

from app.main import app
from app.security import create_access_token

client = TestClient(app, raise_server_exceptions=False)


def _auth(user_id: str = "dev-user") -> dict[str, str]:
    return {"Authorization": f"Bearer {create_access_token(user_id)}"}


AUTH = _auth()
SQUARE = "def square(n):\n    return n * n\n"
GET_LAST = "def get_last(stack):\n    return stack[-1]\n"


def test_lab_get_requires_auth():
    assert client.get("/api/lab/py-101").status_code == 401


def test_lab_get_shape():
    r = client.get("/api/lab/py-101", headers=AUTH)
    assert r.status_code == 200
    body = r.json()
    assert body["lesson_id"] == "py-101"
    assert isinstance(body["prompt"], str) and body["prompt"]
    assert body["test_cases"]
    for t in body["test_cases"]:
        assert set(t) == {"input", "expected"}


def test_lab_get_unknown_and_invalid_ids():
    assert client.get("/api/lab/xx-999", headers=AUTH).status_code == 404
    assert client.get("/api/lab/nope!!", headers=AUTH).status_code == 400


def test_lab_submit_requires_auth():
    r = client.post("/api/lab/submit", json={"lesson_id": "py-101", "code": SQUARE})
    assert r.status_code == 401


def test_lab_submit_roundtrip_shape():
    r = client.post(
        "/api/lab/submit", json={"lesson_id": "py-101", "code": SQUARE}, headers=AUTH
    )
    assert r.status_code == 200
    body = r.json()
    assert body["success"] is True
    assert body["score"] == 100.0
    assert isinstance(body["results"], list)


def test_lab_submit_records_progress_for_caller():
    auth = {"Authorization": f"Bearer {create_access_token('lab-learner')}"}
    r = client.post(
        "/api/lab/submit", json={"lesson_id": "ds-101", "code": GET_LAST}, headers=auth
    )
    assert r.status_code == 200
    assert r.json()["success"] is True
    progress = client.get("/api/progress/lab-learner", headers=auth).json()
    assert any(
        p["lesson_id"] == "ds-101" and p["score"] == 100.0 and p["completed"]
        for p in progress
    )
    # Failed attempts are recorded too, mirroring quiz submit scoring.
    bad = client.post(
        "/api/lab/submit",
        json={"lesson_id": "ds-101", "code": "def get_last(stack):\n    return None\n"},
        headers=auth,
    )
    assert bad.status_code == 200
    assert bad.json()["success"] is False
    progress = client.get("/api/progress/lab-learner", headers=auth).json()
    assert any(
        p["lesson_id"] == "ds-101" and p["score"] == 0.0 and not p["completed"]
        for p in progress
    )


def test_lab_submit_status_codes():
    assert (
        client.post("/api/lab/submit", json={"lesson_id": "py-101"}, headers=AUTH).status_code
        == 422
    )
    assert client.post(
        "/api/lab/submit", json={"lesson_id": "py-101", "code": "x" * 10_001}, headers=AUTH
    ).status_code == 422
    assert client.post(
        "/api/lab/submit", json={"lesson_id": "xx-999", "code": SQUARE}, headers=AUTH
    ).status_code == 404
    assert client.post(
        "/api/lab/submit", json={"lesson_id": "nope!!", "code": SQUARE}, headers=AUTH
    ).status_code == 400
