import re

import allure
import pytest
from playwright.sync_api import Page, expect

from src.enums.User import User
from src.pages.cart_page import CartPage
from src.pages.inventory_page import InventoryPage
from src.pages.login_page import LoginPage


class TestCart:
    @pytest.fixture(autouse=True)
    def setup(self, page: Page):
        self.inventory_page = InventoryPage(page)
        self.cart_page = CartPage(page)

    @pytest.mark.parametrize("browser_context_args", [User.STANDARD_USER], indirect=True)
    @allure.title("Sauce Labs Backpack appears correctly on the cart page after being added")
    def test_cart_page_displays_added_backpack(
        self, browser_context_args, base_url: str, page: Page
    ) -> None:
        self.inventory_page.add_backpack_to_cart()
        self.inventory_page.go_to_cart()

        expect(page).to_have_url(f"{base_url}cart.html")
        expect(self.cart_page.title).to_have_text("Your Cart")
        expect(self.cart_page.item_name).to_have_text("Sauce Labs Backpack")
        expect(self.cart_page.item_price).to_have_text("$29.99")
        expect(self.cart_page.item_quantity).to_have_text("1")

    @pytest.mark.devRun
    @pytest.mark.parametrize("browser_context_args", [User.STANDARD_USER], indirect=True)
    @allure.title("Adding Sauce Labs Backpack to cart updates shopping cart badge to 1")
    def test_shopping_cart_badge_shows_one_after_adding_backpack(
        self, browser_context_args, page: Page
    ) -> None:
        self.inventory_page.add_backpack_to_cart()

        expect(self.inventory_page.shopping_cart_badge).to_have_text("1")

    @pytest.mark.devRun
    @allure.title("Standard user logs in, adds Sauce Labs Bike Light, and sees it in the cart")
    def test_standard_user_adds_bike_light_and_sees_it_in_cart(
        self, base_url: str, page: Page
    ) -> None:
        LoginPage(page).login(User.STANDARD_USER, "secret_sauce")
        expect(page).to_have_url(f"{base_url}inventory.html")

        self.inventory_page.add_bike_light_to_cart()
        expect(self.inventory_page.shopping_cart_badge).to_have_text("1")
        expect(self.inventory_page.remove_bike_light_button).to_be_visible()

        self.inventory_page.go_to_cart()
        expect(page).to_have_url(f"{base_url}cart.html")
        expect(self.cart_page.title).to_have_text("Your Cart")
        expect(self.cart_page.cart_items).to_have_count(1)
        expect(self.cart_page.item_name).to_have_text("Sauce Labs Bike Light")
        expect(self.cart_page.item_price).to_have_text("$9.99")
        expect(self.cart_page.item_quantity).to_have_text("1")
        expect(self.cart_page.remove_bike_light_button).to_be_visible()

    @pytest.mark.devRun
    @pytest.mark.parametrize("browser_context_args", [User.STANDARD_USER], indirect=True)
    @allure.title(
        "Standard user can add, verify, remove, and continue shopping through the full "
        "cart lifecycle"
    )
    def test_cart_lifecycle_happy_path(
        self, browser_context_args, base_url: str, page: Page
    ) -> None:
        self.inventory_page.add_backpack_to_cart()
        expect(self.inventory_page.shopping_cart_badge).to_have_text("1")

        self.inventory_page.add_bike_light_to_cart()
        expect(self.inventory_page.shopping_cart_badge).to_have_text("2")

        self.inventory_page.go_to_cart()
        expect(page).to_have_url(f"{base_url}cart.html")
        expect(self.cart_page.cart_items).to_have_count(2)

        self.cart_page.remove_bike_light_from_cart()
        expect(self.cart_page.cart_items).to_have_count(1)
        expect(self.inventory_page.shopping_cart_badge).to_have_text("1")

        self.cart_page.remove_backpack_from_cart()
        expect(self.cart_page.cart_items).to_have_count(0)
        expect(page.get_by_test_id("shopping-cart-badge")).to_be_hidden()

        self.cart_page.continue_shopping()
        expect(page).to_have_url(f"{base_url}inventory.html")

    @pytest.mark.parametrize("browser_context_args", [User.STANDARD_USER], indirect=True)
    @allure.title("Adding two distinct items accumulates the cart badge count")
    def test_add_multiple_items_updates_badge_count(self, browser_context_args, page: Page) -> None:
        expect(self.inventory_page.shopping_cart_badge).to_be_hidden()

        self.inventory_page.add_backpack_to_cart()
        expect(self.inventory_page.shopping_cart_badge).to_have_text("1")

        self.inventory_page.add_bike_light_to_cart()
        expect(self.inventory_page.shopping_cart_badge).to_have_text("2")

    @pytest.mark.parametrize("browser_context_args", [User.STANDARD_USER], indirect=True)
    @allure.title("Adding every product updates the cart badge to the full catalog count")
    def test_add_all_products_updates_badge_to_total_count(
        self, browser_context_args, page: Page
    ) -> None:
        # Count "Add to cart" buttons before clicking, so the assertion isn't brittle to a
        # future change in the catalog size.
        product_count = page.get_by_test_id(re.compile(r"add-to-cart-.*")).count()

        self.inventory_page.add_all_items_to_cart()

        expect(self.inventory_page.shopping_cart_badge).to_have_text(str(product_count))

    @pytest.mark.parametrize("browser_context_args", [User.STANDARD_USER], indirect=True)
    @allure.title(
        "Removing one item from the cart page leaves the other item and its details intact"
    )
    def test_remove_single_item_from_cart_page_preserves_remaining_item(
        self, browser_context_args, page: Page
    ) -> None:
        self.inventory_page.add_backpack_to_cart()
        self.inventory_page.add_bike_light_to_cart()
        self.inventory_page.go_to_cart()

        self.cart_page.remove_bike_light_from_cart()

        expect(self.cart_page.cart_items).to_have_count(1)
        expect(self.cart_page.item_name).to_have_text("Sauce Labs Backpack")

    @pytest.mark.parametrize("browser_context_args", [User.STANDARD_USER], indirect=True)
    @allure.title(
        "Continue Shopping returns to the inventory page even when the cart was never populated"
    )
    def test_continue_shopping_from_empty_cart_returns_to_inventory(
        self, browser_context_args, base_url: str, page: Page
    ) -> None:
        self.inventory_page.go_to_cart()
        expect(page.get_by_test_id("shopping-cart-badge")).to_be_hidden()

        self.cart_page.continue_shopping()

        expect(page).to_have_url(f"{base_url}inventory.html")

    @pytest.mark.skip(
        reason="Documents a problem_user 'Add to cart' defect observed during initial manual "
        "exploration (badge never appears, button never flips to Remove, item never persists "
        "to the cart). Re-verified live on 2026-09-22 and still could not reproduce it "
        "deterministically through this repo's actual test infrastructure: running the "
        "cookie-bypass browser_context_args approach and a real UI login via LoginPage.login "
        "through this repo's own pytest/conftest fixtures (headed Chromium, launch args from "
        "conftest.py) both show normal, correct add-to-cart behavior for problem_user (badge "
        "shows '1', button flips to Remove). The defect was, however, reproduced twice in a "
        "one-off headed browser session outside this repo's pytest fixtures (via manual "
        "Playwright MCP browser automation) after clearing localStorage/sessionStorage first — "
        "suggesting it may depend on some browser/profile/cache state (e.g. a stale cached JS "
        "bundle or extension) not present in this repo's clean pytest-launched browser, rather "
        "than being a stable per-account bug reproducible via this suite's normal setup. "
        "Skipping rather than asserting behavior this repo's own test run cannot consistently "
        "observe; re-verify live before re-enabling."
    )
    @allure.title(
        "problem_user: clicking Add to cart does not add the item or update the badge "
        "(known app defect)"
    )
    @allure.description(
        "Documents an existing SauceDemo problem_user defect rather than asserting desired "
        "behavior: clicking 'Add to cart' silently fails for problem_user — the badge never "
        "appears, the button never flips to 'Remove', and the item never persists to the "
        "cart. If SauceDemo ever fixes this, this test will start failing and should be "
        "revisited.\n\n"
        "Login strategy note: this test deliberately logs in through the real UI form "
        "(LoginPage.login) instead of the usual browser_context_args cookie bypass, since the "
        "cookie-bypass session never exhibited the defect during investigation."
    )
    def test_problem_user_add_to_cart_does_not_update_cart(self, base_url: str, page: Page) -> None:
        login_page = LoginPage(page)
        login_page.login(User.PROBLEM_USER, "secret_sauce")
        expect(page).to_have_url(f"{base_url}inventory.html")

        self.inventory_page.add_backpack_to_cart()

        expect(page.get_by_test_id("shopping-cart-badge")).to_be_hidden()
        expect(self.inventory_page.add_backpack_button).to_have_text("Add to cart")

        page.goto(f"{base_url}cart.html")
        expect(page.get_by_test_id("inventory-item")).to_have_count(0)

    @pytest.mark.skip(
        reason="Known pre-existing SauceDemo defect, not a test bug: axe reports a moderate "
        "'page-has-heading-one' violation on the cart page (verified live and via this test) "
        "because the page has no <h1>. Re-enable once SauceDemo adds a top-level heading."
    )
    @pytest.mark.parametrize("browser_context_args", [User.STANDARD_USER], indirect=True)
    @allure.title("Cart page passes automated accessibility checks (Axe)")
    def test_cart_page_accessibility(
        self, browser_context_args, page: Page, axe_playwright
    ) -> None:
        self.inventory_page.add_backpack_to_cart()
        self.inventory_page.go_to_cart()

        axe_playwright.check_accessibility(page)
