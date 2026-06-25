"""
login_page.py — Login page object
Uses XPath locators matching the live KESEF app (no data-testid attributes exist).
Navigation goes to BASE_URL (root '/'), NOT '/login' — the app router handles it.
"""
import os
import allure
from playwright.sync_api import Page, expect
from pages.base_page import BasePage

BASE_URL = os.environ.get("BASE_URL", "https://kesef.qa.codezyng.com/")


class LoginPage(BasePage):

    def __init__(self, page: Page):
        super().__init__(page)

    # ── Locators (XPath — live app has no data-testid attributes) ────────────

    @property
    def email_input(self):
        return self.page.locator("//input[@name='email']")

    @property
    def password_input(self):
        return self.page.locator("//input[@name='password']")

    @property
    def sign_in_button(self):
        return self.page.locator("//button[text()='Sign In']")

    @property
    def password_toggle_icon(self):
        return self.page.locator("//*[name()='svg' and contains(@class,'lucide-eye')]")

    @property
    def request_new_password_link(self):
        return self.page.locator("//span[normalize-space()='Request a new one.']")

    @property
    def sign_up_link(self):
        return self.page.locator("//span[normalize-space()='Sign Up']")

    @property
    def send_otp_button(self):
        return self.page.locator("//button[@type='submit' and normalize-space()='Send OTP']")

    # ── Password-reset OTP screen (/otp) ──────────────────────────────────────
    @property
    def otp_boxes(self):
        """The six single-digit OTP input boxes on the verify screen."""
        return self.page.locator("input[type='text']")

    @property
    def verify_otp_button(self):
        return self.page.locator("//button[normalize-space()='Verify OTP']")

    @property
    def resend_otp_link(self):
        return self.page.get_by_text("Resend", exact=False)

    # ── Navigation ────────────────────────────────────────────────────────────

    @allure.step("Navigate to login page")
    def goto(self):
        """Navigate to app root — the SPA router shows the login form there."""
        self.page.goto(BASE_URL)
        self.email_input.wait_for(state="visible", timeout=15000)

    # ── Actions ───────────────────────────────────────────────────────────────

    @allure.step("Login with email and password")
    def login(self, email: str, password: str) -> None:
        """Fill credentials and submit. App does not use OTP in QA environment."""
        self.clear_and_type(self.email_input, email)
        self.clear_and_type(self.password_input, password)
        self.click_when_ready(self.sign_in_button)
        self.wait_for_page_to_be_ready()

    def login_with_otp(self, email: str, password: str, otp: str = "") -> None:
        """Backward-compat alias — OTP not required in QA env, delegates to login()."""
        self.goto()
        self.login(email, password)

    @allure.step("Toggle password visibility")
    def toggle_password_visibility(self):
        self.click_when_ready(self.password_toggle_icon)

    @allure.step("Click 'Request a new one' (forgot password)")
    def click_request_new_password(self):
        self.click_when_ready(self.request_new_password_link)

    @allure.step("Click Sign Up link")
    def go_to_signup(self):
        self.click_when_ready(self.sign_up_link)

    # ── Password-reset OTP actions ──────────────────────────────────────────────
    @allure.step("Open forgot-password page and request an OTP")
    def request_password_reset(self, email: str) -> None:
        """From the login page: open forgot-password, submit email, land on /otp."""
        self.click_request_new_password()
        self.email_input.wait_for(state="visible", timeout=15000)
        self.clear_and_type(self.email_input, email)
        self.click_when_ready(self.send_otp_button)
        # The first OTP request of a run can be slow (cold backend + email send),
        # so allow generous time for the navigation to /otp.
        self.page.wait_for_url("**/otp**", timeout=30000)

    @allure.step("Enter the 6-digit OTP code")
    def enter_otp(self, code: str) -> None:
        """Type a 6-digit code; the first box auto-distributes across all six."""
        self.otp_boxes.first.click()
        self.page.keyboard.type(code)

    @allure.step("Submit the OTP for verification")
    def submit_otp(self) -> None:
        self.click_when_ready(self.verify_otp_button)
        self.wait_for_page_to_be_ready()

    # ── Assertions ────────────────────────────────────────────────────────────

    @allure.step("Assert login page is loaded")
    def assert_login_page_loaded(self):
        expect(self.sign_in_button).to_be_visible()

    @allure.step("Assert Sign In button is visible")
    def assert_sign_in_button_visible(self):
        expect(self.sign_in_button).to_be_visible()
