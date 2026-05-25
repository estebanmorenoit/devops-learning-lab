"""Tests for FastAPI endpoints using TestClient."""

import sys
import json
import tempfile
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).parent.parent))

# Point DATA_DIR at a temp dir so tests don't touch real progress/feedback files
import os
_tmp = tempfile.mkdtemp()
os.environ.setdefault("DATA_DIR", _tmp)

from main import app  # noqa: E402 — must come after env var is set

client = TestClient(app)


# ── Lessons endpoints ─────────────────────────────────────────────────────────

def test_get_lessons_returns_list():
    resp = client.get("/api/lessons")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) > 0


def test_get_lessons_items_have_required_fields():
    resp = client.get("/api/lessons")
    for item in resp.json():
        for field in ("key", "title", "phase", "week", "category", "difficulty"):
            assert field in item, f"Lesson {item.get('key')} missing field '{field}'"


def test_get_lesson_by_key_returns_200():
    lessons = client.get("/api/lessons").json()
    first_key = lessons[0]["key"]
    resp = client.get(f"/api/lessons/{first_key}")
    assert resp.status_code == 200
    data = resp.json()
    assert "sections" in data
    assert data["sections"]


def test_get_lesson_unknown_key_returns_404():
    resp = client.get("/api/lessons/this-key-does-not-exist")
    assert resp.status_code == 404


# ── Progress endpoints ────────────────────────────────────────────────────────

def test_get_progress_returns_dict():
    resp = client.get("/api/progress")
    assert resp.status_code == 200
    assert isinstance(resp.json(), dict)


def test_set_progress_marks_lesson_done():
    lessons = client.get("/api/lessons").json()
    key = lessons[0]["key"]
    resp = client.post(f"/api/progress/{key}", json={"done": True})
    assert resp.status_code == 200
    assert resp.json()["ok"] is True

    progress = client.get("/api/progress").json()
    assert progress.get(key) is True


def test_set_progress_marks_lesson_undone():
    lessons = client.get("/api/lessons").json()
    key = lessons[0]["key"]
    client.post(f"/api/progress/{key}", json={"done": True})
    client.post(f"/api/progress/{key}", json={"done": False})

    progress = client.get("/api/progress").json()
    assert progress.get(key) is False


def test_reset_progress_clears_all():
    lessons = client.get("/api/lessons").json()
    for item in lessons[:3]:
        client.post(f"/api/progress/{item['key']}", json={"done": True})

    resp = client.delete("/api/progress")
    assert resp.status_code == 200
    progress = client.get("/api/progress").json()
    assert progress == {}


# ── Feedback endpoints ────────────────────────────────────────────────────────

def test_get_feedback_returns_dict():
    resp = client.get("/api/feedback")
    assert resp.status_code == 200
    assert isinstance(resp.json(), dict)


def test_set_feedback_up_vote():
    lessons = client.get("/api/lessons").json()
    key = lessons[1]["key"]
    resp = client.post(f"/api/feedback/{key}", json={"vote": "up"})
    assert resp.status_code == 200
    assert resp.json()["vote"] == "up"


def test_set_feedback_down_vote():
    lessons = client.get("/api/lessons").json()
    key = lessons[2]["key"]
    resp = client.post(f"/api/feedback/{key}", json={"vote": "down"})
    assert resp.status_code == 200
    assert resp.json()["vote"] == "down"


def test_set_feedback_toggle_removes_vote():
    lessons = client.get("/api/lessons").json()
    key = lessons[3]["key"]
    client.post(f"/api/feedback/{key}", json={"vote": "up"})
    resp = client.post(f"/api/feedback/{key}", json={"vote": "up"})
    assert resp.json().get("vote") is None


def test_set_feedback_invalid_vote_clears():
    lessons = client.get("/api/lessons").json()
    key = lessons[4]["key"]
    client.post(f"/api/feedback/{key}", json={"vote": "up"})
    resp = client.post(f"/api/feedback/{key}", json={"vote": "invalid"})
    assert resp.json().get("vote") is None
