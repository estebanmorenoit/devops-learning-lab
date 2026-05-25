"""Tests for lesson content schema and registry consistency."""

import json
import sys
from pathlib import Path

import pytest

# Allow importing from the backend package
sys.path.insert(0, str(Path(__file__).parent.parent))

from lessons.registry import LESSON_ORDER, get_all_lessons, get_lesson

CONTENT_DIR = Path(__file__).parent.parent / "lessons" / "content"


# ── Registry consistency ──────────────────────────────────────────────────────

def test_all_registered_lesson_files_exist():
    """Every entry in LESSON_ORDER must have a matching JSON file."""
    missing = []
    for phase, week, key, title, cat, subdir, diff in LESSON_ORDER:
        path = CONTENT_DIR / subdir / f"{key}.json"
        if not path.exists():
            missing.append(str(path.relative_to(CONTENT_DIR.parent.parent)))
    assert not missing, f"Missing lesson files:\n" + "\n".join(missing)


def test_no_unregistered_lesson_files():
    """Every JSON file under content/ must be registered in LESSON_ORDER."""
    registered_keys = {entry[2] for entry in LESSON_ORDER}
    unregistered = [
        str(p.relative_to(CONTENT_DIR))
        for p in CONTENT_DIR.rglob("*.json")
        if p.stem not in registered_keys
    ]
    assert not unregistered, f"Unregistered lesson files:\n" + "\n".join(unregistered)


def test_lesson_keys_are_unique():
    """Lesson keys must be unique across the registry."""
    keys = [entry[2] for entry in LESSON_ORDER]
    duplicates = [k for k in keys if keys.count(k) > 1]
    assert not duplicates, f"Duplicate lesson keys: {set(duplicates)}"


def test_difficulty_values_are_valid():
    """Difficulty must be one of the three accepted values."""
    valid = {"beginner", "intermediate", "advanced"}
    for phase, week, key, title, cat, subdir, diff in LESSON_ORDER:
        assert diff in valid, f"{key}: unknown difficulty '{diff}'"


def test_get_all_lessons_returns_all_entries():
    lessons = get_all_lessons()
    assert len(lessons) == len(LESSON_ORDER)


def test_get_all_lessons_have_required_fields():
    for lesson in get_all_lessons():
        for field in ("key", "title", "phase", "week", "category", "difficulty"):
            assert field in lesson, f"Lesson {lesson.get('key')} missing field '{field}'"


def test_get_lesson_returns_none_for_unknown_key():
    assert get_lesson("this-key-does-not-exist") is None


# ── Per-lesson JSON schema ────────────────────────────────────────────────────

def _iter_lessons():
    """Yield (key, lesson_dict) for every lesson that has a JSON file."""
    for phase, week, key, title, cat, subdir, diff in LESSON_ORDER:
        path = CONTENT_DIR / subdir / f"{key}.json"
        if path.exists():
            yield key, json.loads(path.read_text())


@pytest.mark.parametrize("key,lesson", list(_iter_lessons()))
def test_lesson_has_title(key, lesson):
    assert "title" in lesson and lesson["title"], f"{key}: missing or empty title"


@pytest.mark.parametrize("key,lesson", list(_iter_lessons()))
def test_lesson_has_sections(key, lesson):
    sections = lesson.get("sections", [])
    assert sections, f"{key}: has no sections"


@pytest.mark.parametrize("key,lesson", list(_iter_lessons()))
def test_lesson_sections_have_id_and_type(key, lesson):
    for i, sec in enumerate(lesson.get("sections", [])):
        assert "id" in sec, f"{key}/section[{i}]: missing id"
        assert "type" in sec, f"{key}/section[{i}]: missing type"
        assert sec["type"] in ("lesson", "exercise", "quiz", "challenge"), \
            f"{key}/{sec.get('id')}: unknown type '{sec['type']}'"


@pytest.mark.parametrize("key,lesson", list(_iter_lessons()))
def test_lesson_and_exercise_sections_have_body(key, lesson):
    for sec in lesson.get("sections", []):
        if sec.get("type") in ("lesson", "exercise"):
            has_body = "body" in sec or "content" in sec
            assert has_body, f"{key}/{sec.get('id')}: {sec['type']} missing body/content"
            body = sec.get("body", sec.get("content", ""))
            assert len(body.strip()) >= 10, \
                f"{key}/{sec.get('id')}: body is suspiciously short ({len(body)} chars)"


@pytest.mark.parametrize("key,lesson", list(_iter_lessons()))
def test_quiz_sections_are_valid(key, lesson):
    for sec in lesson.get("sections", []):
        if sec.get("type") != "quiz":
            continue
        sec_id = sec.get("id", "quiz")
        questions = sec.get("questions", [])
        assert questions, f"{key}/{sec_id}: quiz has no questions"
        for j, q in enumerate(questions):
            for field in ("q", "options", "answer", "explanation"):
                assert field in q, f"{key}/{sec_id}/q[{j}]: missing field '{field}'"
            options = q["options"]
            answer = q["answer"]
            assert isinstance(answer, int), \
                f"{key}/{sec_id}/q[{j}]: answer must be an integer index, got {type(answer).__name__}"
            assert 0 <= answer < len(options), \
                f"{key}/{sec_id}/q[{j}]: answer index {answer} out of range (options: {len(options)})"
            assert len(options) >= 2, \
                f"{key}/{sec_id}/q[{j}]: quiz option requires at least 2 choices"


@pytest.mark.parametrize("key,lesson", list(_iter_lessons()))
def test_challenge_sections_are_valid(key, lesson):
    for sec in lesson.get("sections", []):
        if sec.get("type") != "challenge":
            continue
        sec_id = sec.get("id", "challenge")
        for field in ("goal", "hints", "success_criteria"):
            assert field in sec, f"{key}/{sec_id}: challenge missing field '{field}'"
        assert isinstance(sec["hints"], list), f"{key}/{sec_id}: hints must be a list"
        assert isinstance(sec["success_criteria"], list), \
            f"{key}/{sec_id}: success_criteria must be a list"
        assert sec["success_criteria"], f"{key}/{sec_id}: success_criteria is empty"
