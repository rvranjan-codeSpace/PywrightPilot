"""Tests for the student database utilities in `src.utilities.db`."""

import sqlite3
from pathlib import Path

import pytest

from src.utilities.db.database import init_db
from src.utilities.db.generate_synthetic_data import insert_synthetic_students

GENDERS = {"Male", "Female", "Other"}
SECTIONS = {"A", "B", "C", "D"}


@pytest.fixture(autouse=True)
def goto() -> None:
    """Override the browser-based `goto` autouse fixture; DB tests don't need a browser."""


@pytest.fixture(autouse=True)
def attach_playwright_results() -> None:
    """Override the browser-based `attach_playwright_results` autouse fixture."""


@pytest.fixture
def db_path(tmp_path: Path) -> Path:
    """Provide an isolated, throwaway SQLite file path for each test."""
    return tmp_path / "student.db"


def test_init_db_creates_student_table(db_path: Path) -> None:
    """`init_db` should create a `student` table with the expected columns."""
    init_db(db_path)

    connection = sqlite3.connect(db_path)
    try:
        columns = [row[1] for row in connection.execute("PRAGMA table_info(student)")]
    finally:
        connection.close()

    assert columns == ["id", "name", "age", "gender", "class"]


def test_insert_synthetic_students_inserts_requested_row_count(db_path: Path) -> None:
    """`insert_synthetic_students` should insert exactly `count` plausible rows."""
    init_db(db_path)

    insert_synthetic_students(2, db_path)

    connection = sqlite3.connect(db_path)
    try:
        rows = connection.execute("SELECT name, age, gender, class FROM student").fetchall()
    finally:
        connection.close()

    assert len(rows) == 2
    for name, age, gender, class_name in rows:
        assert name
        assert 5 <= age <= 18
        assert gender in GENDERS
        assert class_name[:-1].isdigit()
        assert class_name[-1] in SECTIONS


def test_insert_synthetic_students_raises_when_table_missing(db_path: Path) -> None:
    """`insert_synthetic_students` should error clearly if `student` table doesn't exist."""
    with pytest.raises(RuntimeError, match="student"):
        insert_synthetic_students(1, db_path)
