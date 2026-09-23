import allure
import pytest
from playwright.sync_api import Page, expect

from src.enums.User import User


class TestLogin:
    @pytest.fixture(autouse=True)
    def setup(self, page: Page) -> None:
        self.page = page

    @pytest.mark.devRun
    @allure.title("Login with valid credentials test")
    def test_valid_login(self, base_url: str) -> None:
        username = User.STANDARD_USER.value
        password = "secret_sauce"

        self.page.get_by_test_id("username").fill(username)
        self.page.get_by_test_id("password").fill(password)
        self.page.get_by_test_id("login-button").click()

        expect(self.page).to_have_url(f"{base_url}inventory.html")

    @pytest.mark.parametrize(
        "username, password, expected_error",
        [
            (
                User.STANDARD_USER.value,
                "secret_sauce1",
                "Epic sadface: Username and password do not match any user in this service",
            ),
            (
                User.LOCKED_OUT_USER.value,
                "secret_sauce",
                "Epic sadface: Sorry, this user has been locked out.",
            ),
        ],
        ids=["invalid_password", "locked_user"],
    )
    @allure.title("Login with invalid credentials test")
    def test_login_error(
        self, username: str, password: str, expected_error: str
    ) -> None:
        self.page.get_by_test_id("username").fill(username)
        self.page.get_by_test_id("password").fill(password)
        self.page.get_by_test_id("login-button").click()

        expect(self.page.get_by_test_id("error")).to_have_text(expected_error)
