---
description: Delete all student records from the database
allowed-tools: Read, Bash(uv:*)
---

Argument: $ARGUMENTS is the number of most recently inserted student records
to delete (ranked by id). If empty, delete ALL rows in the `student` table.

The database logic already exists in this project — do not write a new
script.

1. Read src/utilities/db/database.py to confirm the `student` table schema
   and DB_PATH.

2. Read src/utilities/db/clear_data.py to confirm the `delete_all_students()`
   and `delete_last_students(count)` functions and the CLI entry point.

3. From the project root, run:

   uv run python -m src.utilities.db.clear_data $ARGUMENTS

   (with no argument this deletes every row; with a count it deletes only
   the last `count` rows, highest ids first)

4. Report how many records were deleted and the database file path
   (from DB_PATH in database.py).
