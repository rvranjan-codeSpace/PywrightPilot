"""Delete all records from the `student` table.

Run via ``python -m src.utilities.db.delete_data`` after the `student` table has
been created with ``src.utilities.db.database.init_db``.
"""

import sqlite3
from pathlib import Path

from src.utilities.db.database import DB_PATH


def delete_all_students(db_path: Path = DB_PATH) -> int:
    """Delete every row from the `student` table.

    :param db_path: Path to the SQLite database file.
    :return: The number of rows deleted.
    :raises RuntimeError: If the `student` table does not exist yet.
    """
    connection = sqlite3.connect(db_path)
    try:
        cursor = connection.cursor()
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='student'"
        )
        if cursor.fetchone() is None:
            msg = (
                "The 'student' table does not exist. Run "
                "`python -m src.utilities.db.database` first to create it."
            )
            raise RuntimeError(msg)

        cursor.execute("DELETE FROM student")
        connection.commit()
        return cursor.rowcount
    finally:
        connection.close()


if __name__ == "__main__":
    deleted_count = delete_all_students()
    print(f"Deleted {deleted_count} student record(s).")  # noqa: T201
