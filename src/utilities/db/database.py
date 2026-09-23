"""SQLite database setup for the `student` table."""

import sqlite3
from pathlib import Path

DB_PATH: Path = Path(__file__).absolute().parents[3] / "resources" / "db" / "student.db"


def init_db(db_path: Path = DB_PATH) -> None:
    """Create the `student` table if it does not already exist.

    :param db_path: Path to the SQLite database file.
    """
    db_path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(db_path)
    try:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS student (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                age INTEGER NOT NULL,
                gender TEXT NOT NULL,
                class TEXT NOT NULL
            )
            """
        )
        connection.commit()
    finally:
        connection.close()


if __name__ == "__main__":
    init_db()
    print(f"Initialized student table at {DB_PATH}")  # noqa: T201
