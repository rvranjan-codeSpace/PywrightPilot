from dataclasses import dataclass

import allure
from playwright.sync_api import Page


@allure.severity(allure.severity_level.NORMAL)
@allure.story("Cart page behavior")
@dataclass
class CartPage:
    def __init__(self, page: Page):
        self.page = page
        self.title = page.get_by_test_id("title")
        self.cart_items = page.get_by_test_id("inventory-item")
        self.item_quantity = page.get_by_test_id("item-quantity")
        self.item_name = page.get_by_test_id("inventory-item-name")
        self.item_price = page.get_by_test_id("inventory-item-price")
        self.remove_backpack_button = page.get_by_test_id("remove-sauce-labs-backpack")
        self.remove_bike_light_button = page.get_by_test_id("remove-sauce-labs-bike-light")
        self.continue_shopping_button = page.get_by_test_id("continue-shopping")

    @allure.step("Remove Sauce Labs Backpack from cart page")
    def remove_backpack_from_cart(self):
        self.remove_backpack_button.click()

    @allure.step("Remove Sauce Labs Bike Light from cart page")
    def remove_bike_light_from_cart(self):
        self.remove_bike_light_button.click()

    @allure.step("Click Continue Shopping to return to inventory page")
    def continue_shopping(self):
        self.continue_shopping_button.click()
