"""Models layer tests: validation only. No HTTP, no execution."""

import pytest
from pydantic import ValidationError

from app.models import LabSubmit


def test_lab_submit_accepts_valid_payload():
    m = LabSubmit(lesson_id="py-101", code="def square(n):\n    return n * n\n")
    assert m.lesson_id == "py-101"


def test_lab_submit_rejects_missing_and_oversize():
    with pytest.raises(ValidationError):
        LabSubmit(lesson_id="py-101")
    with pytest.raises(ValidationError):
        LabSubmit(lesson_id="py-101", code="x" * 10_001)
    with pytest.raises(ValidationError):
        LabSubmit(lesson_id="", code="x")


def test_lab_submit_rejects_extra_fields():
    with pytest.raises(ValidationError):
        LabSubmit(lesson_id="py-101", code="x", user_id="dev-user")
