"""
<<<<<<< HEAD
tests/test_tc01_login.py — TC-01 through TC-30: Login & Authentication

Verified against the live KESEF QA app (https://kesef.qa.codezyng.com):
  • Login form is at "/" — SPA router serves it at root (no /login route).
  • No OTP on login — valid credentials return JWT cookies immediately → /client-portal.
  • OTP only exists in the password-reset flow (CodeType.PASSWORD_RESET).
  • Errors surface as MUI notistack snackbar (role="alert").
  • Logout: Avatar IconButton (button[aria-haspopup='true'] with .MuiAvatar-root)
    → "Logout" menuitem → navigate('/').
  • Role routing (RoleProtectedRoutes): /add-client denyRoles=[INVESTOR, VIEWER] → /dashboard.

Backend error messages (ResultInfoConstant.kt):
  Invalid creds  → "Invalid/Expired credentials!"
  Wrong OTP      → "Invalid OTP!"
  Expired OTP    → "OTP expired!"

Fixtures (conftest.py):
  fresh_page    — unauthenticated page (login-UI & session tests)
  credentials   — default QA-admin email/password dict
  investor_page — page logged in as investor role (needs INVESTOR_EMAIL + INVESTOR_PASSWORD)
  viewer_page   — page logged in as viewer role   (needs VIEWER_EMAIL + VIEWER_PASSWORD)
  admin_page    — page logged in as admin          (needs ADMIN_EMAIL + ADMIN_PASSWORD)

Role tests (TC-24 to TC-26) are skipped automatically when the required
role-specific env vars are not set.
"""
import os
=======
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
>>>>>>> cd899ac3ad04125b6ba0a3d49432655883356fbc
import re
import pytest
import allure
from playwright.sync_api import expect
from pages.login_page import LoginPage

<<<<<<< HEAD
BASE_URL = os.environ.get("BASE_URL", "https://kesef.qa.codezyng.com/")

_HAS_INVESTOR = bool(os.environ.get("INVESTOR_EMAIL"))
_HAS_VIEWER   = bool(os.environ.get("VIEWER_EMAIL"))

=======
>>>>>>> cd899ac3ad04125b6ba0a3d49432655883356fbc

@allure.suite("01 — Login & Authentication")
@pytest.mark.auth
class TestLogin:

<<<<<<< HEAD
    # ═══════════════════════════════════════════════════════════════
    # BASIC LOGIN FLOW
    # ═══════════════════════════════════════════════════════════════

    @allure.title("TC-01 | Valid login lands on /client-portal")
    @allure.description(
        "Enter registered email + correct password and click Sign In. "
        "Expect immediate JWT-based redirect to /client-portal (no OTP step)."
    )
    @pytest.mark.smoke
    def test_tc01_valid_login_succeeds(self, fresh_page, credentials):
=======
    @allure.title("TC-01 | Valid login lands on the authenticated app (/client-portal)")
    @pytest.mark.smoke
    def test_valid_login_succeeds(self, fresh_page, credentials):
        """email + password (no OTP) authenticates and redirects into the app."""
>>>>>>> cd899ac3ad04125b6ba0a3d49432655883356fbc
        login = LoginPage(fresh_page)
        login.login(credentials["email"], credentials["password"])
        expect(fresh_page).to_have_url(re.compile(r"/client-portal"))

<<<<<<< HEAD
    @allure.title("TC-02 | Invalid password shows error alert and stays on login")
    @allure.description(
        "Enter valid email + wrong password. Expect MUI snackbar containing "
        "'Invalid' or 'credential' and the login form to remain visible."
    )
    def test_tc02_invalid_password_shows_error(self, fresh_page, credentials):
=======
    @allure.title("TC-02 | Invalid password shows error toast and stays on login")
    def test_invalid_password_shows_error(self, fresh_page, credentials):
>>>>>>> cd899ac3ad04125b6ba0a3d49432655883356fbc
        login = LoginPage(fresh_page)
        login.clear_and_type(login.email_input, credentials["email"])
        login.clear_and_type(login.password_input, "WrongPassword999!")
        login.click_when_ready(login.sign_in_button)
<<<<<<< HEAD
        expect(fresh_page.get_by_role("alert")).to_contain_text(
            re.compile(r"Invalid|credential", re.IGNORECASE)
        )
        login.assert_login_page_loaded()

    @allure.title("TC-03 | Invalid email format does not authenticate")
    @allure.description(
        "Enter 'notanemail' (no @), click Sign In. "
        "Expect user to remain on the login page and NOT reach /client-portal."
    )
    def test_tc03_invalid_email_format(self, fresh_page):
        login = LoginPage(fresh_page)
        login.clear_and_type(login.email_input, "notanemail")
        login.clear_and_type(login.password_input, "AnyPassword1!")
        login.click_when_ready(login.sign_in_button)
        fresh_page.wait_for_timeout(1500)
        assert "/client-portal" not in fresh_page.url, \
            "Invalid email format must not result in successful login"
        login.assert_sign_in_button_visible()

    # ═══════════════════════════════════════════════════════════════
    # PASSWORD RESET + OTP FLOW
    # ═══════════════════════════════════════════════════════════════

    @allure.title("TC-04 | Requesting a reset OTP shows the 6-digit verify screen")
    @allure.description(
        "Full forgot-password flow: / → /forgot-password → send OTP → /otp. "
        "Assert /otp URL, 6 input boxes, and Verify OTP button."
    )
    @pytest.mark.flaky(reruns=2, reruns_delay=8)
    def test_tc04_reset_otp_screen_shown(self, fresh_page, credentials):
        login = LoginPage(fresh_page)
        login.request_password_reset(credentials["email"])
        login.assert_on_otp_page()

    @allure.title("TC-05 | Wrong OTP keeps the user on the verify screen")
    @allure.description(
        "Reach /otp via request_password_reset, enter '999999', submit. "
        "Assert the URL remains on /otp (wrong OTP must not advance the user)."
    )
    @pytest.mark.flaky(reruns=2, reruns_delay=8)
    def test_tc05_wrong_otp_stays_on_screen(self, fresh_page, credentials):
=======
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
>>>>>>> cd899ac3ad04125b6ba0a3d49432655883356fbc
        login = LoginPage(fresh_page)
        login.request_password_reset(credentials["email"])
        login.enter_otp("999999")
        login.submit_otp()
        fresh_page.wait_for_timeout(1500)
<<<<<<< HEAD
        assert "/otp" in fresh_page.url, \
            "Wrong OTP must not advance past the verify screen"

    @allure.title("TC-06 | Resend OTP control is present on the verify screen")
    @allure.description(
        "Reach /otp via request_password_reset. Assert the Resend link is visible. "
        "(Clickable only after the 5-minute OtpTimer countdown expires.)"
    )
    @pytest.mark.flaky(reruns=2, reruns_delay=8)
    def test_tc06_resend_otp_is_available(self, fresh_page, credentials):
=======
        assert "/otp" in fresh_page.url, "Wrong OTP must not advance past the verify screen"

    @allure.title("TC-06 | Resend control is available on the OTP screen")
    @pytest.mark.flaky(reruns=2, reruns_delay=8)
    def test_resend_otp_is_available(self, fresh_page, credentials):
>>>>>>> cd899ac3ad04125b6ba0a3d49432655883356fbc
        login = LoginPage(fresh_page)
        login.request_password_reset(credentials["email"])
        expect(login.resend_otp_link.first).to_be_visible()

<<<<<<< HEAD
    # ═══════════════════════════════════════════════════════════════
    # EMPTY FIELD VALIDATION
    # ═══════════════════════════════════════════════════════════════

    @allure.title("TC-07 | Submitting with empty email AND password does not authenticate")
    @allure.description(
        "Click Sign In without entering any credentials. "
        "Expect the user to remain on the login page."
    )
    def test_tc07_empty_email_and_password(self, fresh_page):
        login = LoginPage(fresh_page)
        login.click_when_ready(login.sign_in_button)
        fresh_page.wait_for_timeout(1500)
        assert "/client-portal" not in fresh_page.url, \
            "Empty credentials must not result in a successful login"
        login.assert_sign_in_button_visible()

    @allure.title("TC-08 | Submitting with empty email field does not authenticate")
    @allure.description(
        "Leave email blank, fill password, click Sign In. "
        "Expect to remain on login page."
    )
    def test_tc08_empty_email_field(self, fresh_page, credentials):
        login = LoginPage(fresh_page)
        login.clear_and_type(login.password_input, credentials["password"])
        login.click_when_ready(login.sign_in_button)
        fresh_page.wait_for_timeout(1500)
        assert "/client-portal" not in fresh_page.url, \
            "Empty email must not result in a successful login"
        login.assert_sign_in_button_visible()

    @allure.title("TC-09 | Submitting with empty password field does not authenticate")
    @allure.description(
        "Fill email, leave password blank, click Sign In. "
        "Expect to remain on login page."
    )
    def test_tc09_empty_password_field(self, fresh_page, credentials):
        login = LoginPage(fresh_page)
        login.clear_and_type(login.email_input, credentials["email"])
        login.click_when_ready(login.sign_in_button)
        fresh_page.wait_for_timeout(1500)
        assert "/client-portal" not in fresh_page.url, \
            "Empty password must not result in a successful login"
        login.assert_sign_in_button_visible()

    # ═══════════════════════════════════════════════════════════════
    # FIELD BEHAVIOUR
    # ═══════════════════════════════════════════════════════════════

    @allure.title("TC-10 | Password field masks entered characters")
    @allure.description(
        "Assert that input[name='password'] has type='password' so the "
        "browser renders characters as bullets."
    )
    def test_tc10_password_field_masks_input(self, fresh_page):
        login = LoginPage(fresh_page)
        input_type = login.password_input.get_attribute("type")
        assert input_type == "password", (
            f"Expected password input type='password', got '{input_type}'"
        )

    @allure.title("TC-11 | Email field accepts a valid email address without errors")
    @allure.description(
        "Type a properly formatted email address and assert no MUI inline "
        "validation error (p.MuiFormHelperText-root.Mui-error) appears."
    )
    def test_tc11_email_accepts_valid_format(self, fresh_page):
        login = LoginPage(fresh_page)
        login.clear_and_type(login.email_input, "validuser@example.com")
        fresh_page.wait_for_timeout(500)
        error_count = fresh_page.locator("p.MuiFormHelperText-root.Mui-error").count()
        assert error_count == 0, (
            f"No inline error expected for a valid email, but found {error_count}"
        )

    @allure.title("TC-12 | Email field trims leading and trailing spaces")
    @allure.description(
        "Type the valid email surrounded by spaces ('  user@example.com  '). "
        "The login should succeed, proving the app strips whitespace before "
        "sending the credential to the backend."
    )
    def test_tc12_email_trims_spaces(self, fresh_page, credentials):
        login = LoginPage(fresh_page)
        padded_email = f"  {credentials['email']}  "
        login.clear_and_type(login.email_input, padded_email)
        login.clear_and_type(login.password_input, credentials["password"])
        login.click_when_ready(login.sign_in_button)
        fresh_page.wait_for_url("**/client-portal", timeout=20000)
        expect(fresh_page).to_have_url(re.compile(r"/client-portal"))

    @allure.title("TC-13 | Sign In button requires both fields to be filled")
    @allure.description(
        "Fill only the email field (leave password blank) and click Sign In. "
        "Assert the user does NOT reach /client-portal, confirming the form "
        "enforces that both mandatory fields must have a value."
    )
    def test_tc13_login_button_requires_both_fields(self, fresh_page, credentials):
        login = LoginPage(fresh_page)
        login.clear_and_type(login.email_input, credentials["email"])
        # password is intentionally left empty
        login.click_when_ready(login.sign_in_button)
        fresh_page.wait_for_timeout(1500)
        assert "/client-portal" not in fresh_page.url, (
            "Sign In should not succeed when the password field is empty"
        )

    @allure.title("TC-14 | Pressing Enter in the password field submits the login form")
    @allure.description(
        "Fill both fields and press the Enter key instead of clicking Sign In. "
        "Expect the same JWT redirect to /client-portal."
    )
    @pytest.mark.smoke
    def test_tc14_enter_key_submits_form(self, fresh_page, credentials):
        login = LoginPage(fresh_page)
        login.clear_and_type(login.email_input, credentials["email"])
        login.clear_and_type(login.password_input, credentials["password"])
        fresh_page.keyboard.press("Enter")
        fresh_page.wait_for_url("**/client-portal", timeout=20000)
        expect(fresh_page).to_have_url(re.compile(r"/client-portal"))

    # ═══════════════════════════════════════════════════════════════
    # ERROR STATE BEHAVIOUR
    # ═══════════════════════════════════════════════════════════════

    @allure.title("TC-15 | User remains on login page after a failed login attempt")
    @allure.description(
        "Enter valid email + wrong password, click Sign In. "
        "Assert URL is still the root '/' (login page) and the Sign In button "
        "is still visible — the failed attempt must not navigate away."
    )
    def test_tc15_remains_on_login_after_failed(self, fresh_page, credentials):
        login = LoginPage(fresh_page)
        login.clear_and_type(login.email_input, credentials["email"])
        login.clear_and_type(login.password_input, "WrongPassword999!")
        login.click_when_ready(login.sign_in_button)
        fresh_page.wait_for_timeout(2000)
        assert "/client-portal" not in fresh_page.url, \
            "A failed login must not navigate to /client-portal"
        login.assert_sign_in_button_visible()

    @allure.title("TC-16 | Snackbar error message auto-dismisses after a failed login")
    @allure.description(
        "Trigger an invalid-credentials error. Assert the MUI notistack snackbar "
        "appears, then assert it disappears without user interaction. "
        "(notistack autoHideDuration is set on the backend error handler.)"
    )
    def test_tc16_error_snackbar_auto_dismisses(self, fresh_page, credentials):
        login = LoginPage(fresh_page)
        login.clear_and_type(login.email_input, credentials["email"])
        login.clear_and_type(login.password_input, "WrongPassword999!")
        login.click_when_ready(login.sign_in_button)
        snackbar = fresh_page.get_by_role("alert")
        snackbar.wait_for(state="visible", timeout=6000)
        # notistack autoHideDuration — the snackbar should disappear within ~10 s
        snackbar.wait_for(state="hidden", timeout=12000)

    # ═══════════════════════════════════════════════════════════════
    # NAVIGATION — FORGOT PASSWORD + SIGN-UP
    # ═══════════════════════════════════════════════════════════════

    @allure.title("TC-17 | Forgot Password page loads successfully")
    @allure.description(
        "Click 'Request a new one.' and verify /forgot-password URL loads "
        "with the email input field visible and ready."
    )
    def test_tc17_forgot_password_page_loads(self, fresh_page):
        login = LoginPage(fresh_page)
        login.click_request_new_password()
        expect(fresh_page).to_have_url(re.compile(r"/forgot-password"))
        expect(login.email_input).to_be_visible()

    @allure.title("TC-18 | Send OTP button is visible on Forgot Password page")
    @allure.description(
        "Navigate to /forgot-password and assert the 'Send OTP' submit button "
        "is present and visible."
    )
    def test_tc18_send_otp_visible_on_forgot_password(self, fresh_page):
        login = LoginPage(fresh_page)
        login.click_request_new_password()
        expect(login.send_otp_button).to_be_visible()

    @allure.title("TC-19 | OTP verification page loads after requesting password reset")
    @allure.description(
        "Complete the full forgot-password flow: enter email → Send OTP → /otp. "
        "Assert /otp URL, 6 input boxes, and Verify OTP button are present."
    )
    @pytest.mark.flaky(reruns=2, reruns_delay=8)
    def test_tc19_otp_verification_page_loads(self, fresh_page, credentials):
        login = LoginPage(fresh_page)
        login.request_password_reset(credentials["email"])
        login.assert_on_otp_page()

    @allure.title("TC-20 | Sign Up page loads successfully")
    @allure.description(
        "Click the 'Sign Up' link on the login page. "
        "Expect navigation to /sign-up."
    )
    def test_tc20_signup_page_loads(self, fresh_page):
=======
    @allure.title("TC-07 | Forgot password navigates to reset (Send OTP) page")
    def test_forgot_password_navigation(self, fresh_page):
        login = LoginPage(fresh_page)
        login.click_request_new_password()
        expect(fresh_page).to_have_url(re.compile(r"/forgot-password"))
        expect(login.send_otp_button).to_be_visible()

    @allure.title("TC-08 | Sign-up link navigates to /sign-up")
    def test_signup_link(self, fresh_page):
>>>>>>> cd899ac3ad04125b6ba0a3d49432655883356fbc
        login = LoginPage(fresh_page)
        login.go_to_signup()
        expect(fresh_page).to_have_url(re.compile(r"/sign-up"))

<<<<<<< HEAD
    # ═══════════════════════════════════════════════════════════════
    # SESSION BEHAVIOUR
    # ═══════════════════════════════════════════════════════════════

    @allure.title("TC-21 | Authenticated user is redirected to Client Portal")
    @allure.description(
        "Log in with valid credentials. Assert final URL is /client-portal. "
        "(Duplicate of TC-01 — kept as an explicit traceability anchor.)"
    )
    @pytest.mark.smoke
    def test_tc21_authenticated_redirected_to_client_portal(self, fresh_page, credentials):
        login = LoginPage(fresh_page)
        login.login(credentials["email"], credentials["password"])
        expect(fresh_page).to_have_url(re.compile(r"/client-portal"))

    @allure.title("TC-22 | Session persists after page refresh")
    @allure.description(
        "Log in, then reload the page (F5). "
        "The JWT is stored in a cookie so the SPA should not redirect to login "
        "and the user should remain on /client-portal."
    )
    def test_tc22_session_persists_after_refresh(self, fresh_page, credentials):
        login = LoginPage(fresh_page)
        login.login(credentials["email"], credentials["password"])
        expect(fresh_page).to_have_url(re.compile(r"/client-portal"))
        with allure.step("Reload the page"):
            fresh_page.reload()
            fresh_page.wait_for_load_state("networkidle")
        with allure.step("Assert still authenticated after reload"):
            expect(fresh_page).to_have_url(re.compile(r"/client-portal"))

    @allure.title("TC-23 | Unauthenticated user cannot access protected pages")
    @allure.description(
        "Without logging in, navigate directly to /client-portal. "
        "The SPA route guard should redirect to the root login page."
    )
    def test_tc23_cannot_access_protected_pages_without_login(self, fresh_page):
        login = LoginPage(fresh_page)
        with allure.step("Navigate directly to /client-portal without a session"):
            fresh_page.goto(BASE_URL + "client-portal", wait_until="networkidle")
            fresh_page.wait_for_timeout(1500)
        with allure.step("Assert redirected back to login page"):
            assert "/client-portal" not in fresh_page.url, (
                "Unauthenticated user must not access /client-portal"
            )
            login.assert_sign_in_button_visible()

    # ═══════════════════════════════════════════════════════════════
    # ROLE-BASED ACCESS CONTROL
    # ═══════════════════════════════════════════════════════════════

    @allure.title("TC-24 | Investor role cannot access Add Deal page (/add-client)")
    @allure.description(
        "Log in as Investor and navigate to /add-client. "
        "RoleProtectedRoutes (denyRoles=[INVESTOR, VIEWER]) should redirect to /dashboard."
    )
    @pytest.mark.role_access
    @pytest.mark.skipif(
        not _HAS_INVESTOR,
        reason="INVESTOR_EMAIL env var not set — no dedicated investor credentials available"
    )
    def test_tc24_investor_cannot_access_add_deal(self, investor_page):
        with allure.step("Navigate to /add-client as Investor"):
            investor_page.goto(BASE_URL + "add-client", wait_until="networkidle")
            investor_page.wait_for_timeout(1500)
        with allure.step("Assert redirected away from /add-client"):
            assert "/add-client" not in investor_page.url, (
                "Investor role must not be able to access /add-client"
            )

    @allure.title("TC-25 | Viewer role cannot access Add Deal page (/add-client)")
    @allure.description(
        "Log in as Viewer and navigate to /add-client. "
        "RoleProtectedRoutes should redirect to /dashboard."
    )
    @pytest.mark.role_access
    @pytest.mark.skipif(
        not _HAS_VIEWER,
        reason="VIEWER_EMAIL env var not set — no dedicated viewer credentials available"
    )
    def test_tc25_viewer_cannot_access_add_deal(self, viewer_page):
        with allure.step("Navigate to /add-client as Viewer"):
            viewer_page.goto(BASE_URL + "add-client", wait_until="networkidle")
            viewer_page.wait_for_timeout(1500)
        with allure.step("Assert redirected away from /add-client"):
            assert "/add-client" not in viewer_page.url, (
                "Viewer role must not be able to access /add-client"
            )

    @allure.title("TC-26 | Investor role is redirected to Dashboard for restricted pages")
    @allure.description(
        "Log in as Investor and attempt to navigate to /add-client. "
        "Assert the final URL contains /dashboard (the RoleProtectedRoutes redirect target)."
    )
    @pytest.mark.role_access
    @pytest.mark.skipif(
        not _HAS_INVESTOR,
        reason="INVESTOR_EMAIL env var not set — no dedicated investor credentials available"
    )
    def test_tc26_investor_redirected_to_dashboard(self, investor_page):
        with allure.step("Navigate to /add-client as Investor"):
            investor_page.goto(BASE_URL + "add-client", wait_until="networkidle")
            investor_page.wait_for_timeout(1500)
        with allure.step("Assert final URL is /dashboard"):
            assert "/dashboard" in investor_page.url, (
                f"Expected Investor to be redirected to /dashboard, "
                f"got: {investor_page.url}"
            )

    # ═══════════════════════════════════════════════════════════════
    # LOGOUT BEHAVIOUR
    # ═══════════════════════════════════════════════════════════════

    @allure.title("TC-27 | Logout redirects user to the login page")
    @allure.description(
        "Log in, then click the Avatar menu and select 'Logout'. "
        "Assert navigation back to root '/' with the Sign In button visible "
        "and the success toast 'You have been successfully logged out.' shown."
    )
    def test_tc27_logout_redirects_to_login(self, fresh_page, credentials):
        login = LoginPage(fresh_page)
        with allure.step("Login and confirm redirect to /client-portal"):
            login.login(credentials["email"], credentials["password"])
            expect(fresh_page).to_have_url(re.compile(r"/client-portal"))
        with allure.step("Click Avatar → Logout"):
            login.logout()
        with allure.step("Assert user is back on the login page"):
            login.assert_sign_in_button_visible()
            assert "/client-portal" not in fresh_page.url, \
                "After logout the user must not remain on /client-portal"

    @allure.title("TC-28 | Browser back button does not reopen protected pages after logout")
    @allure.description(
        "Log in → land on /client-portal → logout → press browser back. "
        "The SPA route guard should detect the cleared session and redirect back "
        "to the login page rather than showing /client-portal."
    )
    def test_tc28_back_button_blocked_after_logout(self, fresh_page, credentials):
        login = LoginPage(fresh_page)
        with allure.step("Login and confirm /client-portal"):
            login.login(credentials["email"], credentials["password"])
            expect(fresh_page).to_have_url(re.compile(r"/client-portal"))
        with allure.step("Logout"):
            login.logout()
            login.assert_sign_in_button_visible()
        with allure.step("Press browser Back button"):
            fresh_page.go_back()
            fresh_page.wait_for_load_state("networkidle")
            fresh_page.wait_for_timeout(1500)
        with allure.step("Assert /client-portal is not accessible (back to login)"):
            assert "/client-portal" not in fresh_page.url, (
                "After logout, pressing Back must not reopen the protected /client-portal view"
            )
            login.assert_sign_in_button_visible()

    # ═══════════════════════════════════════════════════════════════
    # PASSWORD VISIBILITY TOGGLE
    # ═══════════════════════════════════════════════════════════════

    @allure.title("TC-29 | Password toggle reveals the masked password")
    @allure.description(
        "Type a password (input starts as type='password'), click the eye "
        "toggle icon, and assert the input switches to type='text' so the "
        "characters become readable."
    )
    def test_tc29_password_toggle_reveals_password(self, fresh_page, credentials):
        login = LoginPage(fresh_page)
        login.clear_and_type(login.password_input, credentials["password"])
        assert login.password_input.get_attribute("type") == "password", \
            "Password field should start masked (type='password')"
        login.toggle_password_visibility()
        expect(login.password_input).to_have_attribute("type", "text")

    @allure.title("TC-30 | Password toggle re-masks the revealed password")
    @allure.description(
        "After revealing the password (type='text'), click the toggle icon "
        "again and assert the input returns to type='password', re-masking the "
        "characters."
    )
    def test_tc30_password_toggle_remasks_password(self, fresh_page, credentials):
        login = LoginPage(fresh_page)
        login.clear_and_type(login.password_input, credentials["password"])
        login.toggle_password_visibility()
        expect(login.password_input).to_have_attribute("type", "text")
        login.toggle_password_visibility()
        expect(login.password_input).to_have_attribute("type", "password")
=======
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
>>>>>>> cd899ac3ad04125b6ba0a3d49432655883356fbc
