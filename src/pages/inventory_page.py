import re
from dataclasses import dataclass

import allure
from playwright.sync_api import Page


@allure.severity(allure.severity_level.NORMAL)
@allure.story("Inventory page behavior")
@dataclass
class InventoryPage:
    def __init__(self, page: Page):
        self.page = page
        self.title = page.get_by_test_id("title")
        self.shopping_cart_badge = page.get_by_test_id("shopping-cart-badge")
        self.shopping_cart_link = page.get_by_test_id("shopping-cart-link")
        self.add_backpack_button = page.get_by_test_id("add-to-cart-sauce-labs-backpack")
        self.remove_backpack_button = page.get_by_test_id("remove-sauce-labs-backpack")
        self.add_bike_light_button = page.get_by_test_id("add-to-cart-sauce-labs-bike-light")
        self.remove_bike_light_button = page.get_by_test_id("remove-sauce-labs-bike-light")

    @allure.step("Add Sauce Labs Backpack to cart from inventory page")
    def add_backpack_to_cart(self):
        self.add_backpack_button.click()

    @allure.step("Remove Sauce Labs Backpack from cart from inventory page")
    def remove_backpack_from_cart(self):
        self.remove_backpack_button.click()

    @allure.step("Add Sauce Labs Bike Light to cart from inventory page")
    def add_bike_light_to_cart(self):
        self.add_bike_light_button.click()

    @allure.step("Remove Sauce Labs Bike Light from cart from inventory page")
    def remove_bike_light_from_cart(self):
        self.remove_bike_light_button.click()

    @allure.step("Add all products to cart from inventory page")
    def add_all_items_to_cart(self):
        # Each click flips that button's data-test id from "add-to-cart-*" to "remove-*", so
        # re-querying and always clicking the first remaining match (rather than snapshotting
        # a fixed list up front, which goes stale as the matching set shrinks) is what keeps
        # this correct as the count decreases to zero.
        add_to_cart_buttons = self.page.get_by_test_id(re.compile(r"add-to-cart-.*"))
        while add_to_cart_buttons.count() > 0:
            add_to_cart_buttons.first.click()

    @allure.step("Navigate to the cart page")
    def go_to_cart(self):
        self.shopping_cart_link.click()
