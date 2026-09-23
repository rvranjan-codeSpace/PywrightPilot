# Cart Feature Test Plan

**Scope:** This constrained plan covers exactly two scenarios: (1) the full happy-path cart
lifecycle — adding items from the inventory page, badge accuracy, removing items from the cart
page, badge accuracy after removal, and returning to inventory via "Continue Shopping" — and
(2) a genuine, reproducible defect discovered while investigating `problem_user`'s "Add to cart"
behavior.

**Target app:** `https://www.saucedemo.com/` (SauceDemo)

## Marker convention used

Per `Playwright-Python-Example/CLAUDE.md` and `tests/CLAUDE.md`, the pre-merge PR gate marker is
**`@pytest.mark.devRun`** (run via `pytest -m devRun`, wired into `.github/workflows/devRun.yml`).
Unmarked tests fall into the nightly sweep (`pytest -m "not devRun"`). This plan uses `devRun`
exactly as found — no new marker was introduced. Scenario 1 (the full-lifecycle happy path) is
marked `devRun`, per the task's instruction to keep the PR gate set small and fast. Scenario 2
(the `problem_user` defect) is unmarked for the nightly run, since it documents an existing
app-level quirk rather than core happy-path behavior.

## Existing coverage (not re-planned here)

- `tests/inventory_test.py::TestInventory::test_add_backpack_to_cart_updates_inventory_page`
  (`devRun`) — already covers adding a single backpack from the inventory page and asserts the
  badge shows `"1"` and the button flips to "Remove". Not duplicated below; Scenario 1 builds on
  top of this by extending into multi-item add/remove/continue-shopping.
- `tests/cart_test.py::TestCart::test_cart_page_displays_added_backpack` — already covers that an
  added backpack renders correctly (name/price/qty) on the cart page itself. Not duplicated below.
- `tests/checkout_test.py::TestCheckout::test_checkout_counter` — sets `cart-contents` directly
  via `localStorage` and asserts the badge shows `"2"` after reload. This is a narrow,
  localStorage-driven check; it does not exercise real add/remove clicks, so it does not overlap
  with the click-driven badge scenario planned below.

## Page objects: existing vs. new methods needed

Only locators/methods actually exercised by Scenario 1 and Scenario 2 are listed below.

### `src/pages/inventory_page.py` (existing)
- Locators: `title`, `shopping_cart_badge`, `shopping_cart_link`, `add_backpack_button`,
  `remove_backpack_button`
- Methods: `add_backpack_to_cart()`, `go_to_cart()`

**New locators/methods needed** (follow the existing per-item, `@allure.step`-decorated
convention — do not introduce a generic locator factory unless a future scenario needs it):
- `add_bike_light_button = page.get_by_test_id("add-to-cart-sauce-labs-bike-light")`
- `add_bike_light_to_cart()` — `@allure.step("Add Sauce Labs Bike Light to cart from inventory page")`

### `src/pages/cart_page.py` (existing)
- Locators: `title`, `cart_items`, `item_quantity`, `item_name`, `item_price`,
  `remove_backpack_button`
- Methods: none (dataclass with locators only)

**New locators/methods needed:**
- `continue_shopping_button = page.get_by_test_id("continue-shopping")`
- `remove_bike_light_button = page.get_by_test_id("remove-sauce-labs-bike-light")`
- `remove_backpack_from_cart()` — `@allure.step("Remove Sauce Labs Backpack from cart page")`, clicks the existing `remove_backpack_button` locator (locator already exists but is currently unused by any method)
- `remove_bike_light_from_cart()` — `@allure.step("Remove Sauce Labs Bike Light from cart page")`
- `continue_shopping()` — `@allure.step("Click Continue Shopping to return to inventory page")`, clicks `continue_shopping_button`

## Live-site findings that shaped this plan

- Verified via manual exploration (`standard_user`): adding two different items increments the
  badge to `"2"`; removing one item from the cart page decrements it correctly; removing the last
  item makes the `shopping-cart-badge` test-id element **disappear entirely** (the cart button's
  accessible name becomes `"Cart, empty"` with no numeric child element) rather than showing
  `"0"`. Tests must assert non-visibility/absence, not text `"0"`.
- Verified `data-test="continue-shopping"` exists on the cart page and, when clicked, navigates
  back to `/inventory.html`.
- **`problem_user` investigation (see Scenario 2 below):** this is a real, reproducible deviation
  worth testing, not a forced-in scenario.

---

## Flow 1: Full cart lifecycle (devRun gate)

### Scenario 1: Standard user can add items, see badge update, remove items, see badge update, and return to inventory via Continue Shopping

- **Target file:** `tests/cart_test.py`
- **Class / function name:** `TestCart::test_cart_lifecycle_happy_path`
- **Login strategy:** Indirect bypass — `@pytest.mark.parametrize("browser_context_args", [User.STANDARD_USER], indirect=True)`; `goto` autouse fixture lands on `/inventory.html`.
- **Marker recommendation:** `@pytest.mark.devRun` — this is the single consolidated happy-path
  test for the whole cart feature (add → badge → remove → badge → continue shopping); per the
  task priority this is the one test in this plan that must gate merges to `main`.
- **Page objects needed:** `InventoryPage` (`add_backpack_to_cart`, `add_bike_light_to_cart` [new], `go_to_cart`, `shopping_cart_badge`), `CartPage` (`remove_bike_light_from_cart` [new], `remove_backpack_from_cart` [new], `item_name`, `cart_items`, `continue_shopping` [new])
- **Allure labels:** `@allure.title("Standard user can add, verify, remove, and continue shopping through the full cart lifecycle")`; steps inherited from the page-object `@allure.step` decorators listed above.
- **Starting state:** Fresh `standard_user` session on `/inventory.html`, empty cart.
- **Steps / expected outcomes:**
  1. Add Sauce Labs Backpack from inventory → `expect(inventory_page.shopping_cart_badge).to_have_text("1")`
  2. Add Sauce Labs Bike Light from inventory → `expect(inventory_page.shopping_cart_badge).to_have_text("2")`
  3. Navigate to cart (`go_to_cart()`) → `expect(page).to_have_url(f"{base_url}cart.html")`; `expect(cart_page.cart_items).to_have_count(2)`
  4. Remove Sauce Labs Bike Light from the cart page → `expect(cart_page.cart_items).to_have_count(1)`; `expect(inventory_page.shopping_cart_badge).to_have_text("1")` (badge is shared header UI, visible on cart page too)
  5. Remove Sauce Labs Backpack from the cart page → `expect(cart_page.cart_items).to_have_count(0)`; `expect(page.get_by_test_id("shopping-cart-badge")).to_be_hidden()` (badge element has no count once cart is empty — see live-site findings)
  6. Click Continue Shopping → `expect(page).to_have_url(f"{base_url}inventory.html")`
- **Success criteria:** All six assertions above pass in sequence within one test.
- **Failure conditions:** Badge shows stale/incorrect count at any step; cart page still lists a removed item; Continue Shopping does not return to `/inventory.html`; badge element is present with text `"0"` instead of being hidden/absent.

---

## Flow 2: `problem_user` investigation

### Scenario 2 (found deviation — worth testing): `problem_user`'s "Add to cart" click does not add the item or update the badge

**Investigation performed:** Logged in live as `problem_user` and repeated the exact add-item
steps used for `standard_user`. Result: clicking "Add to cart" for Sauce Labs Backpack left the
cart badge absent (`"Cart, empty"` accessible name, no `shopping-cart-badge` element), the button
still read "Add to cart" (never flipped to "Remove"), and navigating to `/cart.html` confirmed
the cart was genuinely empty — this was reproduced twice, including a check immediately after
the click (no timing/animation delay involved). This is a real, reproducible,
cart-logic-affecting deviation from `standard_user` — not the commonly-cited image/sort-order
`problem_user` quirks, which are cosmetic and irrelevant here. It is included as genuine
discovered coverage of an app defect, not as coverage-diversity filler. (`error_user` and
`visual_user`, which have other known cart/checkout quirks on the live site, are not usable here
since they are not defined in this repo's `User` `StrEnum` — only `STANDARD_USER`,
`LOCKED_OUT_USER`, `PROBLEM_USER`, and `PERFORMANCE_GLITCH_USER` exist in
`src/enums/User.py`.)

- **Target file:** `tests/cart_test.py`
- **Class / function name:** `TestCart::test_problem_user_add_to_cart_does_not_update_cart`
- **Login strategy:** Indirect bypass — `@pytest.mark.parametrize("browser_context_args", [User.PROBLEM_USER], indirect=True)`
- **Marker recommendation:** unmarked (nightly) — documents a known app-level defect on a
  known-glitchy test user; not core happy-path, and not something that should block every PR
  merge if it (correctly) keeps failing/flagging against the live demo app's existing bug.
- **Page objects needed:** `InventoryPage` (`add_backpack_to_cart`, `shopping_cart_badge`, `add_backpack_button`)
- **Allure labels:** `@allure.title("problem_user: clicking Add to cart does not add the item or update the badge (known app defect)")`; consider `@allure.description` noting this documents existing SauceDemo `problem_user` behavior rather than asserting desired behavior.
- **Starting state:** Fresh `problem_user` session on `/inventory.html`, empty cart.
- **Steps / expected outcomes:**
  1. Click "Add to cart" for Sauce Labs Backpack.
  2. `expect(page.get_by_test_id("shopping-cart-badge")).to_be_hidden()` — badge never appears (this is the defect being documented)
  3. `expect(inventory_page.add_backpack_button).to_have_text("Add to cart")` — button never flips to "Remove"
  4. Navigate to `/cart.html` → `expect(page.get_by_test_id("inventory-item")).to_have_count(0)` — item was never actually persisted to the cart
- **Success criteria:** Test passes if the documented defect persists (badge stays hidden, button stays "Add to cart", cart stays empty). If SauceDemo ever fixes this for `problem_user`, the test will start failing and should be revisited/removed at that point — this is intentional regression coverage for a known quirk, not a "this must always be broken" assertion.
- **Failure conditions (i.e., what would make this test fail, prompting investigation):** Badge appears, button flips to "Remove", or the item shows up on the cart page — any of these would mean SauceDemo's `problem_user` behavior changed and this plan/test needs updating.
- **Note on scope:** `PERFORMANCE_GLITCH_USER` was also considered — its known quirk is added
  latency, not incorrect cart state, so a dedicated cart scenario for it would only be worth
  adding if a slow-loading/timeout-sensitive test is desired; not included here since the
  add/remove/badge/continue-shopping logic itself is unaffected. `LOCKED_OUT_USER` is excluded
  entirely since it cannot reach the inventory/cart pages at all (covered by `login_test.py`).

---

## Summary table

| # | Scenario | File | Marker | New page-object work |
|---|----------|------|--------|----------------------|
| 1 | Full cart lifecycle happy path | `cart_test.py` | `devRun` | `InventoryPage.add_bike_light_to_cart`, `CartPage.remove_bike_light_from_cart`, `CartPage.remove_backpack_from_cart`, `CartPage.continue_shopping` |
| 2 | `problem_user` add-to-cart defect | `cart_test.py` | none | (reuses existing `add_backpack_to_cart`) |
