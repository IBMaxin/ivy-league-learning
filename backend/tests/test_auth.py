"""Auth Phase 2: JWT mint + verify, fail-closed."""

from datetime import UTC, datetime, timedelta

import jwt
from fastapi.testclient import TestClient

from app.config import settings
from app.main import app
from app.security import create_access_token

client = TestClient(app, raise_server_exceptions=False)


def test_mint_and_use_token():
    r = client.post("/api/auth/token", json={"user_id": "dev-user"})
    assert r.status_code == 200
    token = r.json()["access_token"]
    assert r.json()["token_type"] == "bearer"  # noqa: S105 — protocol literal, not a password
    me = client.get("/api/progress/dev-user", headers={"Authorization": f"Bearer {token}"})
    assert me.status_code == 200


def test_mint_rejects_bad_id():
    assert client.post("/api/auth/token", json={"user_id": "nope!!"}).status_code == 400


def test_garbage_token_rejected():
    r = client.get(
        "/api/progress/dev-user", headers={"Authorization": "Bearer dev-token"}
    )
    assert r.status_code == 401


def test_expired_token_rejected():
    now = datetime.now(UTC)
    payload = {
        "sub": "dev-user",
        "iss": settings.jwt_issuer,
        "aud": settings.jwt_audience,
        "iat": now - timedelta(hours=2),
        "exp": now - timedelta(hours=1),
    }
    token = jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)
    r = client.get(
        "/api/progress/dev-user", headers={"Authorization": f"Bearer {token}"}
    )
    assert r.status_code == 401


def test_wrong_audience_rejected():
    token = jwt.encode(
        {
            "sub": "dev-user",
            "iss": settings.jwt_issuer,
            "aud": "someone-else",
            "iat": datetime.now(UTC),
            "exp": datetime.now(UTC) + timedelta(minutes=5),
        },
        settings.jwt_secret,
        algorithm=settings.jwt_algorithm,
    )
    r = client.get(
        "/api/progress/dev-user", headers={"Authorization": f"Bearer {token}"}
    )
    assert r.status_code == 401


def test_cross_user_forbidden_not_unauthorized():
    other = create_access_token("someone-else")
    r = client.get(
        "/api/progress/dev-user", headers={"Authorization": f"Bearer {other}"}
    )
    assert r.status_code == 403
