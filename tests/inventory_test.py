import allure
import pytest
from playwright.sync_api import Page, expect

from src.enums.User import User
from src.pages.inventory_page import InventoryPage


class TestInventory:
    @pytest.fixture(autouse=True)
    def setup(self, page: Page):
        self.inventory_page = InventoryPage(page)

    @pytest.mark.parametrize("browser_context_args", [User.STANDARD_USER], indirect=True)
    def test_inventory_page(self, browser_context_args, page: Page) -> None:
        expect(page.get_by_test_id("title")).to_have_text("Products")

    @pytest.mark.devRun
    @pytest.mark.parametrize("browser_context_args", [User.STANDARD_USER], indirect=True)
    @allure.title("Adding Sauce Labs Backpack updates cart badge and button state")
    def test_add_backpack_to_cart_updates_inventory_page(
        self, browser_context_args, page: Page
    ) -> None:
        self.inventory_page.add_backpack_to_cart()
        expect(self.inventory_page.shopping_cart_badge).to_have_text("1")
        expect(self.inventory_page.remove_backpack_button).to_be_visible()

    @pytest.mark.parametrize("browser_context_args", [User.STANDARD_USER], indirect=True)
    @allure.title(
        "Removing Sauce Labs Backpack from the inventory page reverts button state and "
        "clears the badge"
    )
    def test_remove_backpack_from_cart_updates_inventory_page(
        self, browser_context_args, page: Page
    ) -> None:
        self.inventory_page.add_backpack_to_cart()
        expect(self.inventory_page.shopping_cart_badge).to_have_text("1")

        self.inventory_page.remove_backpack_from_cart()

        expect(page.get_by_test_id("shopping-cart-badge")).to_be_hidden()
        expect(self.inventory_page.add_backpack_button).to_be_visible()
