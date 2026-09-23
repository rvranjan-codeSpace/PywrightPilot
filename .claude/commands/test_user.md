---
description: Create N synthetic student records in the database
allowed-tools: Read, Bash(uv:*)
---

Argument: $ARGUMENTS is the number of student records to create. If empty, default to 1.

The database logic already exists in this project — do not write a new script.

1. Read src/utilities/db/database.py to confirm the `student` table schema
   and the `init_db()` helper.

2. Read src/utilities/db/generate_synthetic_data.py to confirm the
   `insert_synthetic_students(count)` function and its CLI entry point.

3. From the project root, ensure the `student`
   table exists:

   uv run python -m src.utilities.db.database

4. Insert $ARGUMENTS synthetic student record(s):

   uv run python -m src.utilities.db.generate_synthetic_data $ARGUMENTS

5. Report how many records were inserted and the database file path
   (from DB_PATH in database.py).
