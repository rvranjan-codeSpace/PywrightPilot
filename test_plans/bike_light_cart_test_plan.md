# Bike Light Add-to-Cart Test Plan

**Scope:** A single end-to-end scenario: log in to SauceDemo as `standard_user` through the real
login form, add **Sauce Labs Bike Light** to the cart, open the cart, and verify the Bike Light is
the item in the cart.

**Target app:** `https://www.saucedemo.com/` (SauceDemo)

## Existing coverage (not re-planned here)

- `tests/cart_test.py::TestCart::test_cart_page_displays_added_backpack` covers the same
  add → cart → verify details flow, but for the **Backpack** and with the cookie login bypass.
- `tests/cart_test.py::TestCart::test_cart_lifecycle_happy_path` adds the Bike Light alongside the
  Backpack and checks only the item count (`2`). It never checks the Bike Light's name, price or
  quantity on the cart page.
- The gap this plan fills: no current test checks that the Bike Light alone shows up with the
  right details in the cart after a **real UI login**.

## Live-site findings (verified 2026-09-24)

| Step | Observed |
|---|---|
| Login `standard_user` / `secret_sauce` | Redirects to `/inventory.html` |
| Click `add-to-cart-sauce-labs-bike-light` | Badge `shopping-cart-badge` shows `1`; button flips to `remove-sauce-labs-bike-light` ("Remove") |
| Click `shopping-cart-link` | Navigates to `/cart.html`, title "Your Cart" |
| Cart contents | 1 row: name **Sauce Labs Bike Light**, price **$9.99**, qty **1**, "Remove" button present |

## Page objects

All required locators and methods already exist, so **no page-object changes are needed**:

- `src/pages/login_page.py` → `LoginPage.login(User.STANDARD_USER, "secret_sauce")`
- `src/pages/inventory_page.py` → `add_bike_light_to_cart()`, `go_to_cart()`,
  `shopping_cart_badge`, `remove_bike_light_button`
- `src/pages/cart_page.py` → `title`, `cart_items`, `item_name`, `item_price`, `item_quantity`,
  `remove_bike_light_button`

## Flow 1: Add Bike Light to cart and verify in cart

### Scenario 1.1: Standard user logs in, adds the Bike Light, and sees it in the cart

- **Target file:** `tests/cart_test.py` (existing)
- **Class / function:** `TestCart.test_standard_user_adds_bike_light_and_sees_it_in_cart`
- **Login strategy:** real UI login through `LoginPage.login()`. The request explicitly includes
  logging in, so the test does **not** parametrize `browser_context_args`. Without that
  parametrization, the autouse `goto` fixture opens the login page.
- **Marker:** `@pytest.mark.devRun`. This is a short, critical happy path (login + add + cart)
  and belongs in the pre-merge gate.
- **Allure title:** `"Standard user logs in, adds Sauce Labs Bike Light, and sees it in the cart"`
- **Starting state:** fresh browser context, empty cart, on the login page.

**Steps and assertions:**

| # | Step | Expected (`expect`) |
|---|---|---|
| 1 | `LoginPage(page).login(User.STANDARD_USER, "secret_sauce")` | `expect(page).to_have_url(f"{base_url}inventory.html")` |
| 2 | `inventory_page.add_bike_light_to_cart()` | `expect(inventory_page.shopping_cart_badge).to_have_text("1")`<br>`expect(inventory_page.remove_bike_light_button).to_be_visible()` |
| 3 | `inventory_page.go_to_cart()` | `expect(page).to_have_url(f"{base_url}cart.html")`<br>`expect(cart_page.title).to_have_text("Your Cart")` |
| 4 | Verify the cart contents | `expect(cart_page.cart_items).to_have_count(1)`<br>`expect(cart_page.item_name).to_have_text("Sauce Labs Bike Light")`<br>`expect(cart_page.item_price).to_have_text("$9.99")`<br>`expect(cart_page.item_quantity).to_have_text("1")`<br>`expect(cart_page.remove_bike_light_button).to_be_visible()` |

**Success criteria:** every assertion passes, and the cart holds exactly one item, the Bike Light,
with the correct price and quantity.

**Failure conditions:** the login does not redirect to inventory, the badge is missing or not `1`,
the cart is empty or holds a different or extra item, or the price or quantity does not match.

### Reference implementation sketch

```python
@pytest.mark.devRun
@allure.title("Standard user logs in, adds Sauce Labs Bike Light, and sees it in the cart")
def test_standard_user_adds_bike_light_and_sees_it_in_cart(self, base_url: str, page: Page) -> None:
    LoginPage(page).login(User.STANDARD_USER, "secret_sauce")
    expect(page).to_have_url(f"{base_url}inventory.html")

    self.inventory_page.add_bike_light_to_cart()
    expect(self.inventory_page.shopping_cart_badge).to_have_text("1")

    self.inventory_page.go_to_cart()
    expect(page).to_have_url(f"{base_url}cart.html")
    expect(self.cart_page.cart_items).to_have_count(1)
    expect(self.cart_page.item_name).to_have_text("Sauce Labs Bike Light")
    expect(self.cart_page.item_price).to_have_text("$9.99")
    expect(self.cart_page.item_quantity).to_have_text("1")
```
