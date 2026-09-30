"""Services layer tests: pure orchestration. No HTTP, no auth, no DB."""

from app.services import validate_lab

SQUARE = "def square(n):\n    return n * n\n"


def test_validate_lab_success_shape():
    body = validate_lab("py-101", SQUARE)
    assert body["success"] is True
    assert body["score"] == 100.0
    assert body["correct"] == body["total"] == 3
    assert body["results"]
    assert all(set(r) >= {"input", "expected", "passed"} for r in body["results"])


def test_validate_lab_wrong_code_is_failure_not_error():
    body = validate_lab("py-101", "def square(n):\n    return 0\n")
    assert body["success"] is False
    assert body["score"] == 0.0
    assert body["correct"] == 0
    assert body["results"]  # logic failure surfaces as results, not "error"


def test_validate_lab_unknown_lesson():
    body = validate_lab("xx-999", SQUARE)
    assert body == {"success": False, "error": "Lab not found"}


def test_lab_submit_syntax_surfaces_as_unsuccessful():
    body = validate_lab("py-101", "def square(n):\n    return n *\n")
    assert body["success"] is False
    assert body["score"] == 0.0
    assert body["results"] == []
