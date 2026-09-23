"""Fill the `student` table with synthetic data.

Run via ``python -m src.utilities.db.generate_synthetic_data <count>`` after the
`student` table has been created with ``src.utilities.db.database.init_db``.
"""

import argparse
import sqlite3
from pathlib import Path
from random import choice, randint

from faker import Faker

from src.utilities.db.database import DB_PATH

GENDERS: list[str] = ["Male", "Female", "Other"]
GRADE_LEVELS: range = range(1, 13)
SECTIONS: list[str] = ["A", "B", "C", "D"]

fake = Faker()


def generate_student_row() -> tuple[str, int, str, str]:
    """Generate a single synthetic student record.

    :return: A `(name, age, gender, class_name)` tuple.
    """
    name = fake.name()
    age = randint(5, 18)  # noqa: S311
    gender = choice(GENDERS)  # noqa: S311
    class_name = f"{choice(GRADE_LEVELS)}{choice(SECTIONS)}"  # noqa: S311
    return name, age, gender, class_name


def insert_synthetic_students(count: int, db_path: Path = DB_PATH) -> None:
    """Insert `count` synthetic student records into the `student` table.

    :param count: Number of synthetic student records to insert.
    :param db_path: Path to the SQLite database file.
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

        rows = [generate_student_row() for _ in range(count)]
        cursor.executemany(
            "INSERT INTO student (name, age, gender, class) VALUES (?, ?, ?, ?)",
            rows,
        )
        connection.commit()
    finally:
        connection.close()


def main() -> None:
    """Parse CLI arguments and insert the requested number of synthetic students."""
    parser = argparse.ArgumentParser(
        description="Fill the student database with synthetic data."
    )
    parser.add_argument(
        "count", type=int, help="Number of synthetic student records to insert."
    )
    args = parser.parse_args()

    insert_synthetic_students(args.count)
    print(f"Inserted {args.count} synthetic student record(s).")  # noqa: T201


if __name__ == "__main__":
    main()
