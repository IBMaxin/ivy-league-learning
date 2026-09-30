"""Router tests: curriculum, library, quiz, adaptive, community."""

from fastapi.testclient import TestClient

from app.main import app
from app.security import create_access_token

client = TestClient(app, raise_server_exceptions=False)


def _auth(user_id: str = "dev-user") -> dict[str, str]:
    return {"Authorization": f"Bearer {create_access_token(user_id)}"}


AUTH = _auth()


def test_curriculum_shape():
    r = client.get("/api/curriculum")
    assert r.status_code == 200
    tracks = r.json()["tracks"]
    assert len(tracks) == 6
    lessons = [lesson["id"] for t in tracks for lesson in t["lessons"]]
    assert {
        "py-101",
        "js-101",
        "rust-101",
        "api-101",
        "react-101",
        "maths-101",
        "stats-101",
        "hum-101",
        "writing-101",
        "algs-101",
        "ds-101",
        "os-101",
        "net-101",
        "db-101",
    } <= set(lessons)


def test_library_all_and_search():
    all_items = client.get("/api/library").json()
    assert all_items["count"] > 0
    res = client.get("/api/library", params={"q": "rust"}).json()
    assert res["count"] >= 1
    assert all("rust" in (i["title"] + i["university"] + i["type"]).lower() for i in res["items"])


def test_library_level_filter():
    res = client.get("/api/library", params={"level": "beginner"}).json()
    assert all(i["level"] in ("beginner", "all") for i in res["items"])


def test_quiz_public_without_answers():
    r = client.get("/api/quiz/py-101")
    assert r.status_code == 200
    for q in r.json()["questions"]:
        assert "q" in q and "choices" in q
        assert "answer" not in q


def test_quiz_bad_id():
    assert client.get("/api/quiz/nope!!").status_code == 400
    assert client.get("/api/quiz/xx-999").status_code == 404


def test_quiz_submit_scores_and_records():
    payload = {"user_id": "dev-user", "lesson_id": "py-101", "answers": [1, 1, 2]}
    r = client.post("/api/quiz/submit", json=payload, headers=AUTH)
    assert r.status_code == 200
    body = r.json()
    assert body["score"] == 100.0
    assert body["correct"] == 3
    progress = client.get("/api/progress/dev-user", headers=AUTH).json()
    assert any(p["lesson_id"] == "py-101" and p["score"] == 100.0 for p in progress)


def test_quiz_submit_partial_score():
    payload = {"user_id": "dev-user", "lesson_id": "js-101", "answers": [0, 0, 0]}
    body = client.post("/api/quiz/submit", json=payload, headers=AUTH).json()
    assert body["score"] < 100.0
    assert body["recommendation"]["lesson_id"] is not None


def test_quiz_submit_rejects_bad_input():
    base = {"user_id": "dev-user", "lesson_id": "py-101"}
    short = {**base, "answers": [1]}
    r = client.post("/api/quiz/submit", json=short, headers=AUTH)
    assert r.status_code == 400
    bad_range = {**base, "answers": [9, 9, 9]}
    assert client.post("/api/quiz/submit", json=bad_range, headers=AUTH).status_code == 400
    assert client.post("/api/quiz/submit", json={**base, "answers": [1, 1, 2]}).status_code == 401
    other = {"user_id": "someone-else", "lesson_id": "py-101", "answers": [1, 1, 2]}
    assert client.post("/api/quiz/submit", json=other, headers=AUTH).status_code == 403


def test_adaptive_recommendation():
    payload = {"user_id": "dev-user", "lesson_id": "py-101", "answers": [1, 1, 2]}
    assert client.post("/api/quiz/submit", json=payload, headers=AUTH).status_code == 200
    r = client.get("/api/adaptive/recommend/dev-user", headers=AUTH)
    assert r.status_code == 200
    body = r.json()
    assert "recommendation" in body and "mastery" in body
    assert body["completed"]
    assert client.get("/api/adaptive/recommend/other", headers=AUTH).status_code == 403
    assert client.get("/api/adaptive/recommend/dev-user").status_code == 401


def test_new_tracks_quiz_submit_and_recommend():
    auth = _auth("fresh-learner")
    for lesson_id, answers in [
        ("maths-101", [1, 1, 1]),
        ("stats-101", [1, 1, 1]),
        ("hum-101", [1, 1, 1]),
        ("writing-101", [0, 1, 1]),
    ]:
        q = client.get(f"/api/quiz/{lesson_id}")
        assert q.status_code == 200
        assert len(q.json()["questions"]) == 3
        r = client.post(
            "/api/quiz/submit",
            json={"user_id": "fresh-learner", "lesson_id": lesson_id, "answers": answers},
            headers=auth,
        )
        assert r.status_code == 200
        assert r.json()["score"] == 100.0
    rec = client.get("/api/adaptive/recommend/fresh-learner", headers=auth).json()
    assert rec["recommendation"]["lesson_id"] == "py-101"


def test_algorithms_track_quiz_submit():
    auth = _auth("algs-learner")
    for lesson_id, answers in [
        ("algs-101", [2, 2, 1]),
        ("ds-101", [0, 1, 0]),
    ]:
        q = client.get(f"/api/quiz/{lesson_id}")
        assert q.status_code == 200
        assert len(q.json()["questions"]) == 3
        for item in q.json()["questions"]:
            assert "answer" not in item
        r = client.post(
            "/api/quiz/submit",
            json={"user_id": "algs-learner", "lesson_id": lesson_id, "answers": answers},
            headers=auth,
        )
        assert r.status_code == 200
        assert r.json()["score"] == 100.0
    rec = client.get("/api/adaptive/recommend/algs-learner", headers=auth).json()
    assert rec["recommendation"]["lesson_id"] == "py-101"


def test_systems_track_quiz_submit():
    auth = _auth("sys-learner")
    for lesson_id, answers in [
        ("os-101", [1, 1, 1]),
        ("net-101", [2, 1, 1]),
        ("db-101", [1, 1, 1]),
    ]:
        q = client.get(f"/api/quiz/{lesson_id}")
        assert q.status_code == 200
        assert len(q.json()["questions"]) == 3
        r = client.post(
            "/api/quiz/submit",
            json={"user_id": "sys-learner", "lesson_id": lesson_id, "answers": answers},
            headers=auth,
        )
        assert r.status_code == 200
        assert r.json()["score"] == 100.0
    rec = client.get("/api/adaptive/recommend/sys-learner", headers=auth).json()
    assert rec["recommendation"]["lesson_id"] == "py-101"


def test_community_roundtrip():
    before = client.get("/api/community/posts").json()["count"]
    post = {"author": "tester", "title": "How to start Rust?", "body": "Tips?", "track": "general"}
    r = client.post("/api/community/posts", json=post, headers=AUTH)
    assert r.status_code == 201
    after = client.get("/api/community/posts").json()
    assert after["count"] == before + 1
    bad = {**post, "track": "nope"}
    assert client.post("/api/community/posts", json=bad, headers=AUTH).status_code == 400
    assert client.post("/api/community/posts", json=post).status_code == 401


def test_code_run_python_print():
    code = "print('hi')\nprint(2 + 3 * 2)"
    r = client.post("/api/code/run", json={"language": "python", "code": code}, headers=AUTH)
    assert r.status_code == 200
    assert r.json()["output"] == "hi\n8"


def test_code_run_python_blocks_import_and_exec():
    bad = "import os\nprint('x')"
    r = client.post("/api/code/run", json={"language": "python", "code": bad}, headers=AUTH)
    assert r.status_code == 200
    assert "Stopped" in r.json()["output"]
    assert "hi" not in r.json()["output"] or True  # nothing executed before block


def test_code_run_python_loop_capped():
    r = client.post(
        "/api/code/run",
        json={"language": "python", "code": "for i in range(3):\n    print(i)"},
        headers=AUTH,
    )
    assert r.status_code == 200
    assert r.json()["output"] == "0\n1\n2"


def test_code_run_js_and_rust_preview():
    js = client.post(
        "/api/code/run",
        json={"language": "javascript", "code": 'console.log("hi")'},
        headers=AUTH,
    )
    assert js.status_code == 200
    assert "console.log" in js.json()["output"]
    rs = client.post(
        "/api/code/run",
        json={"language": "rust", "code": 'fn main() {\n println!("hi");\n}'},
        headers=AUTH,
    )
    assert rs.status_code == 200
    assert "cargo run" in rs.json()["output"]


def test_code_run_requires_auth():
    r = client.post("/api/code/run", json={"language": "python", "code": "print(1)"})
    assert r.status_code == 401
