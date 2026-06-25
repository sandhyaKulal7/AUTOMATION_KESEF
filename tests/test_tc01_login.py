"""
test_tc01_login.py — TC-01 through TC-10: Login & Authentication

Verified against the live KESEF QA app (https://kesef.qa.codezyng.com):
  • Login form is at "/" (no "/login" route)
  • No OTP step on login — a valid login returns tokens immediately and
    lands on /client-portal. (OTP only exists in the password-reset flow.)
  • Errors are shown via a react-toastify toast (".Toastify__toast-body")
  • "Request a new one." -> /forgot-password   ;   "Sign Up" -> /sign-up

Login-UI tests use the UNauthenticated `fresh_page` fixture, not `page`
(which auto-logs-in via conftest).
"""
import re
import pytest
import allure
from playwright.sync_api import expect
from pages.login_page import LoginPage


@allure.suite("01 — Login & Authentication")
@pytest.mark.auth
class TestLogin:

    @allure.title("TC-01 | Valid login lands on the authenticated app (/client-portal)")
    @pytest.mark.smoke
    def test_valid_login_succeeds(self, fresh_page, credentials):
        """email + password (no OTP) authenticates and redirects into the app."""
        login = LoginPage(fresh_page)
        login.login(credentials["email"], credentials["password"])
        expect(fresh_page).to_have_url(re.compile(r"/client-portal"))

    @allure.title("TC-02 | Invalid password shows error toast and stays on login")
    def test_invalid_password_shows_error(self, fresh_page, credentials):
        login = LoginPage(fresh_page)
        login.clear_and_type(login.email_input, credentials["email"])
        login.clear_and_type(login.password_input, "WrongPassword999!")
        login.click_when_ready(login.sign_in_button)
        # Error surfaces as a notistack MUI snackbar (role="alert")
        expect(fresh_page.get_by_role("alert")).to_contain_text(
            re.compile(r"Invalid|credential", re.IGNORECASE)
        )
        login.assert_login_page_loaded()  # still on login page

    @allure.title("TC-03 | Invalid email format does not authenticate")
    def test_invalid_email_format(self, fresh_page):
        login = LoginPage(fresh_page)
        login.clear_and_type(login.email_input, "notanemail")
        login.clear_and_type(login.password_input, "anypassword")
        login.click_when_ready(login.sign_in_button)
        fresh_page.wait_for_timeout(1500)
        assert "/client-portal" not in fresh_page.url, \
            "Invalid email must not authenticate"
        login.assert_sign_in_button_visible()

    # NOTE: This app has NO OTP on login (tokens return immediately). OTP exists
    # only in the password-reset flow, so TC-04..06 cover that flow instead.

    @allure.title("TC-04 | Requesting a reset OTP shows the 6-digit verify screen")
    @pytest.mark.flaky(reruns=2, reruns_delay=8)
    def test_reset_otp_screen_shown(self, fresh_page, credentials):
        login = LoginPage(fresh_page)
        login.request_password_reset(credentials["email"])
        expect(fresh_page).to_have_url(re.compile(r"/otp"))
        expect(login.otp_boxes).to_have_count(6)
        expect(login.verify_otp_button).to_be_visible()

    @allure.title("TC-05 | Wrong OTP keeps the user on the verify screen")
    @pytest.mark.flaky(reruns=2, reruns_delay=8)
    def test_wrong_otp_stays_on_screen(self, fresh_page, credentials):
        login = LoginPage(fresh_page)
        login.request_password_reset(credentials["email"])
        login.enter_otp("999999")
        login.submit_otp()
        fresh_page.wait_for_timeout(1500)
        assert "/otp" in fresh_page.url, "Wrong OTP must not advance past the verify screen"

    @allure.title("TC-06 | Resend control is available on the OTP screen")
    @pytest.mark.flaky(reruns=2, reruns_delay=8)
    def test_resend_otp_is_available(self, fresh_page, credentials):
        login = LoginPage(fresh_page)
        login.request_password_reset(credentials["email"])
        expect(login.resend_otp_link.first).to_be_visible()

    @allure.title("TC-07 | Forgot password navigates to reset (Send OTP) page")
    def test_forgot_password_navigation(self, fresh_page):
        login = LoginPage(fresh_page)
        login.click_request_new_password()
        expect(fresh_page).to_have_url(re.compile(r"/forgot-password"))
        expect(login.send_otp_button).to_be_visible()

    @allure.title("TC-08 | Sign-up link navigates to /sign-up")
    def test_signup_link(self, fresh_page):
        login = LoginPage(fresh_page)
        login.go_to_signup()
        expect(fresh_page).to_have_url(re.compile(r"/sign-up"))

    @allure.title("TC-09 | Investor sees limited menu")
    @pytest.mark.role_access
    @pytest.mark.skip(reason="No dedicated investor credentials available yet; "
                             "role would fall back to admin and invalidate the assertion.")
    def test_investor_sees_limited_menu(self):
        pass

    @allure.title("TC-10 | Viewer cannot access Add Deal")
    @pytest.mark.role_access
    @pytest.mark.skip(reason="No dedicated viewer credentials available yet; "
                             "role would fall back to admin and invalidate the assertion.")
    def test_viewer_cannot_add_deal(self):
        pass
