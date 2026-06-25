"""
pages/login_page.py — Login & Auth page object for the KESEF portal.

Covers three screens:
  1. Login  (/)                          – email / password / Sign In
  2. Forgot Password  (/forgot-password) – email / Send OTP
  3. OTP Verify  (/otp)                  – 6-box OTP / Verify / Resend

Key facts from source analysis
──────────────────────────────
• App root '/' IS the login page — do NOT navigate to /login.
• Login has NO OTP step; JWT is returned immediately on valid credentials.
• OTP workflow is for password-reset only (backend CodeType.PASSWORD_RESET).
• OTP is a 6-digit code, expires after 5 minutes (OtpTimer component).
• "Forgot Password" link text on login page: "Request a new one."
• "Sign Up" link text on login page: "Sign Up" (inside a <span>).
• Verify OTP button text: "Verify OTP"
• Backend error texts (surfaces as MUI notistack role="alert"):
    invalid creds  → "Invalid/Expired credentials!"
    wrong OTP      → "Invalid OTP!"
    expired OTP    → "OTP expired!"
• Sidebar 'Add Deal' (/add-client) is disabled for Investor + Viewer roles
  (RoleProtectedRoutes denyRoles=[INVESTOR, VIEWER] → redirect to /dashboard).
"""

import os
import allure
from playwright.sync_api import Page, Locator, expect
from pages.base_page import BasePage

BASE_URL = os.environ.get("BASE_URL", "https://kesef.qa.codezyng.com/")


class LoginPage(BasePage):

    def __init__(self, page: Page):
        super().__init__(page)

    # ── Locators — Login page (/) ─────────────────────────────────────────────
    # XPath only; live app has zero data-testid attributes.

    @property
    def email_input(self) -> Locator:
        return self.page.locator("//input[@name='email']")

    @property
    def password_input(self) -> Locator:
        return self.page.locator("//input[@name='password']")

    @property
    def sign_in_button(self) -> Locator:
        return self.page.locator("//button[text()='Sign In']")

    @property
    def password_toggle_icon(self) -> Locator:
        return self.page.locator("//*[name()='svg' and contains(@class,'lucide-eye')]")

    @property
    def request_new_password_link(self) -> Locator:
        """'Request a new one.' link on the login page (Forgot Password)."""
        return self.page.locator("//span[normalize-space()='Request a new one.']")

    # Alias used in tests and conftest helpers
    @property
    def forgot_password_link(self) -> Locator:
        return self.request_new_password_link

    @property
    def sign_up_link(self) -> Locator:
        return self.page.locator("//span[normalize-space()='Sign Up']")

    # ── Locators — Forgot-Password page (/forgot-password) ───────────────────
    # email_input reuses the same XPath (name="email").

    @property
    def send_otp_button(self) -> Locator:
        """'Send OTP' submit button on /forgot-password."""
        return self.page.locator("//button[@type='submit' and normalize-space()='Send OTP']")

    # ── Locators — OTP-Verify page (/otp) ────────────────────────────────────

    @property
    def otp_boxes(self) -> Locator:
        """
        The six individual single-character OTP input boxes.
        The live app renders each box with aria-label='Please enter OTP character N'
        (no maxlength attribute), so we match on that aria-label prefix — more
        specific than input[type='text'], which would also match other fields.
        """
        return self.page.locator("//input[contains(@aria-label,'enter OTP character')]")

    @property
    def verify_otp_button(self) -> Locator:
        return self.page.locator("//button[normalize-space()='Verify OTP']")

    @property
    def resend_otp_link(self) -> Locator:
        """Resend link rendered by OtpTimer; clickable only after countdown expires."""
        return self.page.get_by_text("Resend", exact=False)

    # ── Locators — Sidebar (for role-access tests) ────────────────────────────
    # MUI ListItemButton items; 'Add Deal' maps to /add-client.

    @property
    def sidebar_add_deal_link(self) -> Locator:
        return self.page.locator("//a[@href='/add-client']")

    @property
    def sidebar_dashboard_link(self) -> Locator:
        return self.page.locator("//a[@href='/dashboard']")

    @property
    def sidebar_reports_link(self) -> Locator:
        # "Reports" can be a collapsible group (button) rather than a direct link
        return self.page.locator(
            "//span[text()='Reports'] | //a[contains(text(),'Reports')]"
        )

    # ── Navigation ────────────────────────────────────────────────────────────

    @allure.step("Navigate to login page")
    def goto(self, path: str = "/") -> None:
        """Navigate to app root — the SPA router renders the login form there."""
        self.page.goto(BASE_URL + path.lstrip("/"))
        self.email_input.wait_for(state="visible", timeout=15000)

    # ── Login-page actions ────────────────────────────────────────────────────

    @allure.step("Login with email and password")
    def login(self, email: str, password: str) -> None:
        """
        Fill credentials and click Sign In.
        Waits for the post-login redirect to /client-portal.
        No OTP step — the app issues JWT cookies directly on success.
        """
        self.clear_and_type(self.email_input, email)
        self.clear_and_type(self.password_input, password)
        self.click_when_ready(self.sign_in_button)
        # Explicit URL wait is more reliable than networkidle for SPA redirects.
        self.page.wait_for_url("**/client-portal", timeout=20000)
        self.page.wait_for_load_state("networkidle", timeout=15000)

    def login_with_otp(self, email: str, password: str, otp: str = "") -> None:
        """Backward-compat alias — no OTP on login in QA env; delegates to login()."""
        self.goto()
        self.login(email, password)

    @allure.step("Toggle password visibility")
    def toggle_password_visibility(self) -> None:
        self.click_when_ready(self.password_toggle_icon)

    @allure.step("Click 'Request a new one.' (Forgot Password)")
    def click_request_new_password(self) -> None:
        """Click the Forgot-Password link and wait for /forgot-password to load."""
        self.click_when_ready(self.request_new_password_link)
        # Wait for the Send OTP button on the forgot-password screen instead of URL navigation
        # — SPA routing may not trigger a full navigation.
        self.send_otp_button.wait_for(state="visible", timeout=20000)

    @allure.step("Click Sign Up link")
    def go_to_signup(self) -> None:
        """Click the Sign Up link and wait for /sign-up to load."""
        self.click_when_ready(self.sign_up_link)
        self.page.wait_for_url("**/sign-up", timeout=10000)

    # ── Forgot-password + OTP actions ────────────────────────────────────────

    @allure.step("Open forgot-password page and request an OTP")
    def request_password_reset(self, email: str) -> None:
        """
        Full forgot-password flow from the login page to /otp:
          / → click 'Request a new one.'
          → /forgot-password: fill email → click Send OTP
          → /otp (OTP-Verify screen)

        The first OTP request of a test run can be slow (cold backend + email
        send), so a 30-second timeout is used for the final URL wait.
        """
        self.click_request_new_password()
        self.email_input.wait_for(state="visible", timeout=15000)
        self.clear_and_type(self.email_input, email)
        self.click_when_ready(self.send_otp_button)
        # Save the resulting page HTML to help debug OTP rendering issues.
        try:
            self.page.wait_for_load_state("networkidle", timeout=10000)
        except Exception:
            pass
        try:
            html = self.page.content()
            out_dir = os.path.join(os.getcwd(), "reports", "screenshots")
            os.makedirs(out_dir, exist_ok=True)
            out_path = os.path.join(out_dir, "otp_page.html")
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(html)
        except Exception:
            pass

        # The app may take time to process the OTP request. Wait for the OTP
        # verify UI (Verify OTP button) up to 45s rather than relying solely
        # on a URL change — SPA routing can be delayed.
        try:
            # Prefer checking for the Verify OTP button as the most reliable
            # indicator that the OTP screen is ready.
            expect(self.verify_otp_button).to_be_visible(timeout=45000)
        except Exception:
            # As a fallback, try URL-based wait for /otp for the same period.
            self.page.wait_for_url("**/otp**", timeout=45000)
        finally:
            try:
                self.page.wait_for_load_state("networkidle", timeout=10000)
            except Exception:
                pass

    @allure.step("Enter the 6-digit OTP code")
    def enter_otp(self, code: str) -> None:
        """
        Type a 6-digit OTP.
        Uses keyboard.type() so the first focused box propagates the keystrokes
        across all six boxes automatically (standard React OTP input behaviour).
        """
        self.otp_boxes.first.wait_for(state="visible", timeout=10000)
        self.otp_boxes.first.click()
        self.page.keyboard.type(code)

    @allure.step("Submit OTP (click Verify OTP)")
    def submit_otp(self) -> None:
        self.click_when_ready(self.verify_otp_button)
        self.wait_for_page_to_be_ready()

    @allure.step("Click Resend OTP")
    def click_resend_otp(self) -> None:
        """
        Click the Resend link on /otp.
        Only interactive after the 5-minute OtpTimer countdown has reached 00:00.
        """
        self.click_when_ready(self.resend_otp_link.first)

    # ── Assertion helpers ─────────────────────────────────────────────────────

    @allure.step("Assert login page is loaded")
    def assert_login_page_loaded(self) -> None:
        """Assert the login form is still visible — user has not navigated away."""
        expect(self.sign_in_button).to_be_visible()
        expect(self.email_input).to_be_visible()

    @allure.step("Assert Sign In button is visible")
    def assert_sign_in_button_visible(self) -> None:
        expect(self.sign_in_button).to_be_visible()

    @allure.step("Assert OTP-Verify page is shown")
    def assert_on_otp_page(self) -> None:
        """Assert /otp URL, 6 input boxes, and Verify OTP button are all present."""
        import re
        expect(self.page).to_have_url(re.compile(r"/otp"))
        expect(self.otp_boxes).to_have_count(6)
        expect(self.verify_otp_button).to_be_visible()