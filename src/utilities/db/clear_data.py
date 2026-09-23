"""Delete records from the `student` table.

Run via ``python -m src.utilities.db.clear_data [count]`` after the `student`
table has been created with ``src.utilities.db.database.init_db``. With no
`count`, every row is deleted; with `count`, only the `count` most recently
inserted rows (highest ids) are deleted.
"""

import argparse
import sqlite3
from pathlib import Path

from src.utilities.db.database import DB_PATH


def _table_exists(cursor: sqlite3.Cursor) -> bool:
    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='student'"
    )
    return cursor.fetchone() is not None


def delete_all_students(db_path: Path = DB_PATH) -> int:
    """Delete every row from the `student` table.

    :param db_path: Path to the SQLite database file.
    :return: The number of rows deleted.
    :raises RuntimeError: If the `student` table does not exist yet.
    """
    connection = sqlite3.connect(db_path)
    try:
        cursor = connection.cursor()
        if not _table_exists(cursor):
            msg = (
                "The 'student' table does not exist. Run "
                "`python -m src.utilities.db.database` first to create it."
            )
            raise RuntimeError(msg)

        cursor.execute("DELETE FROM student")
        deleted = cursor.rowcount
        connection.commit()
        return deleted
    finally:
        connection.close()


def delete_last_students(count: int, db_path: Path = DB_PATH) -> int:
    """Delete the `count` most recently inserted rows from the `student` table.

    :param count: Number of most-recently-inserted rows to delete, ranked by id.
    :param db_path: Path to the SQLite database file.
    :return: The number of rows actually deleted.
    :raises RuntimeError: If the `student` table does not exist yet.
    """
    connection = sqlite3.connect(db_path)
    try:
        cursor = connection.cursor()
        if not _table_exists(cursor):
            msg = (
                "The 'student' table does not exist. Run "
                "`python -m src.utilities.db.database` first to create it."
            )
            raise RuntimeError(msg)

        cursor.execute(
            "DELETE FROM student WHERE id IN "
            "(SELECT id FROM student ORDER BY id DESC LIMIT ?)",
            (count,),
        )
        deleted = cursor.rowcount
        connection.commit()
        return deleted
    finally:
        connection.close()


def main() -> None:
    """Parse CLI arguments and delete student record(s) accordingly."""
    parser = argparse.ArgumentParser(
        description="Delete records from the student database."
    )
    parser.add_argument(
        "count",
        type=int,
        nargs="?",
        default=None,
        help=(
            "Number of most recently inserted records to delete. "
            "If omitted, all records are deleted."
        ),
    )
    args = parser.parse_args()

    if args.count is None:
        deleted = delete_all_students()
    else:
        deleted = delete_last_students(args.count)
    print(f"Deleted {deleted} student record(s).")  # noqa: T201


if __name__ == "__main__":
    main()
