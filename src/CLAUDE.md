# CLAUDE.md (src/)

Guidance for working inside `src/`. See the [repo-level CLAUDE.md](../CLAUDE.md) for setup, test commands, and CI. This file covers conventions for the application/support code, not the tests themselves.

## Layout

- `src/pages/` — Page Object Model classes for the SauceDemo UI.
- `src/enums/` — `StrEnum` definitions for test data (e.g. `User`).
- `src/utilities/` — Cross-cutting helpers (constants, accessibility checks, SQLite db utilities).
- `src/utilities/db/` — Standalone SQLite utilities for the `student` table (unrelated to the Playwright suite; used by `tests/db_test.py` and the `test_user`/`delete_user` slash commands).

## Conventions

### Page objects (`src/pages/`)

- One class per page, named `<Thing>Page` (e.g. `LoginPage`), taking a Playwright `Page` in `__init__`.
- Locate elements with `page.get_by_test_id(...)`, matching the `data-test` attribute (registered as the test-id selector in `tests/conftest.py`). Don't use CSS/XPath selectors unless a `data-test` attribute isn't available.
- Decorate action methods with `@allure.step("...")` using `{param}` placeholders so steps render readably in the Allure report.
- Decorate the class with `@allure.severity(...)` and `@allure.story(...)` to classify it for reporting.
- Accept `Union[User, str]` for username-like parameters (see `LoginPage.login`), unwrapping `.value` when a `User` enum is passed, so tests can pass either an enum member or a raw string.

### Enums (`src/enums/`)

- Use `StrEnum` with `auto()` members named in upper snake case; the generated string value is the lowercase member name (e.g. `User.STANDARD_USER == "standard_user"`), matching SauceDemo's actual login usernames.
- Add new test users/data here rather than hardcoding strings in tests.

### Utilities (`src/utilities/`)

- `constants.py` — Add shared literals (paths, tolerances, user agent strings) to the `Constants` class rather than scattering magic values across tests/pages.
- `axe_helper.py` — `AxeHelper.check_accessibility(page, maximum_allowed_violations_by_impact=None)` is the only entry point for accessibility checks; it defaults to zero tolerance for every impact level and attaches violations JSON to Allure on failure. Don't call `Axe()` directly in tests — use the `axe_playwright` fixture from `tests/conftest.py`.

### DB utilities (`src/utilities/db/`)

- All modules resolve the SQLite file via `DB_PATH` in `database.py` (`resources/db/student.db`) but accept an optional `db_path: Path` override — tests always pass an isolated `tmp_path` rather than touching the real db.
- Each script is runnable standalone (`python -m src.utilities.db.<module>`) and also exposes plain functions for import; keep both working when editing.
- Functions that operate on the `student` table should raise `RuntimeError` with a message pointing at `database.init_db` when the table doesn't exist yet (see `clear_data.py`, `delete_data.py`, `generate_synthetic_data.py`) — don't let them fail with a raw `sqlite3.OperationalError`.
- `clear_data.py` and `delete_data.py` overlap (`delete_all_students`); `clear_data.py` is the newer, CLI-argument-aware version (`count` arg to delete only the most recent N rows). Prefer extending `clear_data.py` for new deletion behavior.
