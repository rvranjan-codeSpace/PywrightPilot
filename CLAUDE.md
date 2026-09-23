# CLAUDE.md (tests/)

Guidance for working inside `tests/`. See the [repo-level CLAUDE.md](../CLAUDE.md) for setup and run commands. This file covers conventions for writing/editing tests and fixtures here.

## Layout

- `conftest.py` — shared fixtures for the whole suite (browser/context args, login bypass, Allure attachments on failure). Read this before adding a fixture elsewhere — most cross-cutting behavior belongs here, not in a test file.
- `login_test.py`, `inventory_test.py`, `checkout_test.py` — UI tests against SauceDemo, using Playwright + Page Object Model classes from `src/pages/`.
- `db_test.py` — non-browser tests for `src/utilities/db/`; overrides the browser-only autouse fixtures (see below).

## Conventions

### Bypassing login

Tests that don't need to exercise the login flow itself should indirectly parametrize `browser_context_args` with a `User` enum value instead of calling `LoginPage.login()`:

```python
@pytest.mark.parametrize("browser_context_args", [User.STANDARD_USER], indirect=True)
def test_something(self, browser_context_args, page: Page) -> None:
    ...
```

This injects a `session-username` cookie via `conftest.py`'s `browser_context_args` fixture, and the autouse `goto` fixture then navigates straight to `/inventory.html` instead of the login page. See `inventory_test.py` and `checkout_test.py`.

### Test structure

- Group related tests in a `Test<Thing>` class; use an autouse `setup` fixture to instantiate page objects (see `login_test.py`).
- Use `@allure.title("...")` on tests and `@allure.step("...")` inside page-object methods so the Allure report reads well — don't rely on the raw function name.
- Use `@pytest.mark.devRun` for tests that must run pre-merge (CI gate on PRs into `main`); omit it for tests that should only run in the nightly `not devRun` sweep. Don't mark everything `devRun` — it slows down the PR gate.
- Use `expect(...)` (Playwright's auto-retrying assertion) rather than plain `assert` for anything that reads page/element state.
- Parametrize with `pytest.mark.parametrize(..., ids=[...])` when cases aren't self-describing from their values (see `test_login_error` in `login_test.py`).

### Non-browser tests (`db_test.py` pattern)

Tests that don't drive a browser (e.g. `db_test.py`) must locally override the two browser-dependent autouse fixtures to no-ops, otherwise they'll fail trying to use a `page` fixture that was never requested:

```python
@pytest.fixture(autouse=True)
def goto() -> None: ...

@pytest.fixture(autouse=True)
def attach_playwright_results() -> None: ...
```

Give each such test its own isolated resource (e.g. `db_path` fixture built on `tmp_path`) rather than touching the real `resources/db/student.db`.

### Fixtures in `conftest.py`

- `browser_context_args` and `browser_type_launch_args` extend (not replace) the base Playwright fixtures of the same name — always spread `**browser_context_args`/`**browser_type_launch_args` when adding new context/launch options so existing behavior (user agent, permissions, headed/maximized launch, `data-test` id attribute) isn't lost.
- `attach_playwright_results` depends on `request.node.rep_call`, which is populated by the `pytest_runtest_makereport` hook — don't remove that hook if this fixture is still in use.
- New fixtures that should apply to every test go here; fixtures specific to one test file's concerns can live in that file instead.
