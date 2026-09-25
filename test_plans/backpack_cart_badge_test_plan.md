# Backpack Cart Badge Test Plan

## Add to cart flow

### Scenario 1: Adding Sauce Labs Backpack updates the cart badge to "1"

- **Target file**: `tests/cart_test.py`
- **Class / function name**: `TestCart` (existing class) / `test_shopping_cart_badge_shows_one_after_adding_backpack`
- **Login strategy**: Bypass — `@pytest.mark.parametrize("browser_context_args", [User.STANDARD_USER], indirect=True)`
- **Marker recommendation**: `@pytest.mark.devRun` — happy-path critical add-to-cart flow, must gate PRs
- **Page objects needed**:
  - `InventoryPage.add_backpack_to_cart()` (existing)
  - `InventoryPage.shopping_cart_badge` locator (existing)
  - No new page object methods required
- **Allure labels**: `@allure.title("Adding Sauce Labs Backpack to cart updates shopping cart badge to 1")`
- **Starting state assumption**: Fresh session on `/inventory.html` via login bypass, empty cart (badge not present)
- **Steps**:
  1. Call `self.inventory_page.add_backpack_to_cart()`
- **Expected outcome**: `expect(self.inventory_page.shopping_cart_badge).to_have_text("1")`
- **Success criteria**: Badge locator is visible and text equals `"1"`
- **Failure conditions**: Badge absent, text not `"1"`, or assertion times out
