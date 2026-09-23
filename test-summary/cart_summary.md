# Cart Feature — Test Summary

**Scope:** SauceDemo cart feature. This was a deliberately narrow, constrained plan covering
exactly two scenarios (not a broad sweep): (1) the full `standard_user` cart lifecycle, and
(2) a `problem_user` "Add to cart" defect investigation.

**Date:** 2026-09-22

**Source plan:** [`test_plans/cart_test_plan.md`](../test_plans/cart_test_plan.md)

## Scenario coverage table

| # | Scenario | Target test | Marker | Status | Note |
|---|----------|--------------|--------|--------|------|
| 1 | `standard_user` full cart lifecycle: add backpack + bike light → badge "1" → "2" → go to cart → remove bike light (badge "1") → remove backpack (badge hidden) → Continue Shopping back to inventory | `cart_test.py::TestCart::test_cart_lifecycle_happy_path` | `devRun` | ✅ passed | Verified in my own run; all six sequential assertions (add/badge/remove/badge/continue-shopping) pass. Matches plan's marker recommendation (devRun, PR gate). |
| 2 | `problem_user` "Add to cart" defect investigation (badge never appears, button never flips to Remove, item never persists) | `cart_test.py::TestCart::test_problem_user_add_to_cart_does_not_update_cart` | none (nightly, per plan) | ⏭️ skipped | Skip reason (verbatim, abridged): defect was originally observed via manual exploration, but re-verification today (2026-09-22) through this repo's actual pytest/Playwright infrastructure — both the cookie-bypass `browser_context_args` login and a real UI login via `LoginPage.login` — shows normal, correct `problem_user` add-to-cart behavior (badge shows "1", button flips to Remove). The defect reproduced only in a one-off manual Playwright MCP browser session outside the repo's pytest fixtures, suggesting a browser/profile/cache-state dependency not present in this suite's clean pytest-launched browser. Left skipped rather than force-passed or force-failed, pending live re-verification. |

Both scenarios are implemented as planned; no planned scenario is missing a corresponding test,
and no test in scope improvises beyond the plan.

## Files touched

- `tests/cart_test.py` — per the generator's own report, only the skip reason on
  `test_problem_user_add_to_cart_does_not_update_cart` was refined with today's re-verification
  findings; `test_cart_lifecycle_happy_path` required no edits (already matched the plan). I did
  not independently diff against a prior version, but confirmed the current file content matches
  the plan's structure (see below).
- No page-object files were modified per the generator's report. I confirmed by reading
  `src/pages/inventory_page.py` and `src/pages/cart_page.py`: all locators/methods the plan called
  "new" (`InventoryPage.add_bike_light_to_cart`, `CartPage.remove_backpack_from_cart`,
  `CartPage.remove_bike_light_from_cart`, `CartPage.continue_shopping_button` /
  `continue_shopping()`) are present, `@allure.step`-decorated, and use `get_by_test_id`, per
  repo convention — consistent with them already existing prior to this plan's generation pass
  (or having been added in an earlier, unreported step). No discrepancy found.

## Verification run

Targeted run (this plan's two scenarios only):
```
pytest tests/cart_test.py::TestCart::test_cart_lifecycle_happy_path tests/cart_test.py::TestCart::test_problem_user_add_to_cart_does_not_update_cart -v
```
Result: **1 passed, 1 skipped** in 10.31s.

Full-file run (for context on pre-existing tests outside this plan's scope):
```
pytest tests/cart_test.py -v
```
Result: **6 passed, 2 skipped**, 0 failed, 8 collected, in 34.55s.
- The 6 passes include this plan's Scenario 1 plus 5 pre-existing tests not covered by this plan
  (`test_cart_page_displays_added_backpack`, `test_add_multiple_items_updates_badge_count`,
  `test_add_all_products_updates_badge_to_total_count`,
  `test_remove_single_item_from_cart_page_preserves_remaining_item`,
  `test_continue_shopping_from_empty_cart_returns_to_inventory`).
- The 2 skips are this plan's Scenario 2 (`problem_user` defect, see above) and one unrelated,
  pre-existing skip (`test_cart_page_accessibility`, skipped for a known SauceDemo axe
  `page-has-heading-one` violation on the cart page — out of scope for this plan, not conflated
  with Scenario 2).

## Gaps / follow-ups

- Scenario 2 (`problem_user` defect) is a genuinely-investigated app-level defect that is not
  reproducible via this repo's real pytest/Playwright infrastructure as of today
  (2026-09-22) — reproduced only in an ad hoc manual MCP browser session. Left skipped rather
  than forced to a false pass/fail. Follow-up: re-verify live periodically; if it remains
  unreproducible through the repo's own test infra, consider removing or reframing the test
  (e.g. as an explicitly-marked exploratory/manual note) rather than leaving it skipped
  indefinitely.
- No scenario from the plan is missing a test; no unplanned scenario was added to `cart_test.py`
  within this plan's stated scope.

## Marker balance

This plan added Scenario 1 as `devRun` (1 new devRun test) and Scenario 2 as unmarked/nightly
(currently skipped, 0 effective nightly runs until re-enabled). This matches the plan's own
guidance: keep the devRun/PR-gate set small (one consolidated happy-path test) and route the
known-defect investigation to the nightly, non-blocking sweep.
