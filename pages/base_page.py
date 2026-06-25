"""
base_page.py
All page objects inherit from BasePage.
Contains shared utilities: navigation, waits, element helpers.
No test logic here — only reusable browser interactions.
"""
import allure
from playwright.sync_api import Page, Locator, expect


class BasePage:
    def __init__(self, page: Page):
        self.page = page

    # ── Navigation ────────────────────────────────────────────────────────────
    def goto(self, path: str = "/"):
        with allure.step(f"Navigate to {path}"):
            self.page.goto(path)
            self.page.wait_for_load_state("networkidle")

    def current_url(self) -> str:
        return self.page.url

    # ── Element waits (NO hard waits — all smart waits) ──────────────────────
    def wait_for_selector(self, selector: str, state: str = "visible") -> Locator:
        return self.page.wait_for_selector(selector, state=state)

    def wait_for_text(self, text: str):
        self.page.wait_for_selector(f"text={text}", state="visible")

    def wait_for_url(self, pattern: str):
        self.page.wait_for_url(f"**{pattern}**")

    def wait_for_network_idle(self):
        self.page.wait_for_load_state("networkidle")

    def wait_for_timeout(self, ms: int):
        self.page.wait_for_timeout(ms)

    # ── Click helpers ─────────────────────────────────────────────────────────
    def click(self, selector: str):
        with allure.step(f"Click: {selector}"):
            self.page.locator(selector).click()

    def click_button(self, label: str):
        with allure.step(f"Click button: {label}"):
            self.page.get_by_role("button", name=label).click()

    def click_text(self, text: str):
        with allure.step(f"Click text: {text}"):
            self.page.get_by_text(text, exact=True).click()

    # ── Locator-based helpers (used by page objects with @property locators) ──
    def click_when_ready(self, locator):
        """Wait for a Locator to be actionable, then click it."""
        with allure.step("Click when ready"):
            locator.wait_for(state="visible")
            locator.scroll_into_view_if_needed()
            locator.click()

    def clear_and_type(self, locator, value: str):
        """Wait for a Locator, clear any existing value, then type the new value."""
        with allure.step(f"Clear and type '{value}'"):
            locator.wait_for(state="visible")
            locator.click()
            locator.fill("")
            locator.fill(value)

    def wait_for_page_to_be_ready(self):
        """Wait for network to settle after a navigation/submit (SPA-friendly)."""
        self.page.wait_for_load_state("networkidle")

    # ── Fill helpers ──────────────────────────────────────────────────────────
    def fill(self, selector: str, value: str):
        with allure.step(f"Fill '{selector}' with '{value}'"):
            loc = self.page.locator(selector)
            loc.clear()
            loc.fill(value)

    def fill_by_label(self, label: str, value: str):
        with allure.step(f"Fill field '{label}' with '{value}'"):
            self.page.get_by_label(label).fill(value)

    def fill_by_placeholder(self, placeholder: str, value: str):
        with allure.step(f"Fill placeholder '{placeholder}'"):
            self.page.get_by_placeholder(placeholder).fill(value)

    # ── Select / dropdown helpers ─────────────────────────────────────────────
    def select_mui_dropdown(self, label: str, option_text: str):
        """Select from a Material UI Select/Autocomplete dropdown."""
        with allure.step(f"Select '{option_text}' from '{label}'"):
            self.page.get_by_label(label).click()
            self.page.get_by_role("option", name=option_text).click()

    def select_autocomplete(self, placeholder: str, value: str):
        with allure.step(f"Autocomplete '{placeholder}' = '{value}'"):
            field = self.page.get_by_placeholder(placeholder)
            field.click()
            field.fill(value)
            self.page.get_by_role("option", name=value).first.click()

    # ── Assertion helpers ─────────────────────────────────────────────────────
    def assert_visible(self, selector: str):
        expect(self.page.locator(selector)).to_be_visible()

    def assert_text(self, selector: str, text: str):
        expect(self.page.locator(selector)).to_have_text(text)

    def assert_url_contains(self, fragment: str):
        expect(self.page).to_have_url(f"**{fragment}**")

    def assert_toast(self, message: str):
        """Assert a MUI Snackbar/toast notification."""
        expect(self.page.get_by_role("alert")).to_contain_text(message)

    def assert_not_visible(self, selector: str):
        expect(self.page.locator(selector)).not_to_be_visible()

    # ── Screenshots ───────────────────────────────────────────────────────────
    def screenshot(self, name: str):
        with allure.step(f"Screenshot: {name}"):
            allure.attach(
                self.page.screenshot(full_page=True),
                name=name,
                attachment_type=allure.attachment_type.PNG,
            )

    # ── Logout ───────────────────────────────────────────────────────────────
    def logout(self) -> None:
        """
        Logout via the Avatar menu in the AppBar (ProfileSettings.tsx).
        Flow:
          1. Click the Avatar IconButton (button[aria-haspopup='true'] holding
             a .MuiAvatar-root — the live app has no aria-controls on it).
          2. Click the 'Logout' <MenuItem> in the MUI Menu (sibling 'Profile').
          3. Wait for navigate('/') — the login page.
        On success the app shows 'You have been successfully logged out.' toast.
        """
        with allure.step("Logout via Avatar → Logout menu item"):
            self.page.locator(
                "button[aria-haspopup='true']:has(.MuiAvatar-root)"
            ).first.click()
            self.page.get_by_role("menuitem", name="Logout").click()
            self.page.wait_for_url("**/", timeout=15000)
            self.page.wait_for_load_state("networkidle", timeout=10000)

    # ── Sidebar navigation ────────────────────────────────────────────────────
    # The real KESEF sidebar is a MUI List. Direct items are <a href> links;
    # "Reports" and "Control Panel" are collapsible groups (role=button) that
    # reveal sub-links when clicked. (Verified against the live QA app.)
    def _click_sidebar_link(self, name: str):
        self.page.get_by_role("link", name=name, exact=True).first.click()

    def _expand_sidebar_group(self, name: str):
        self.page.get_by_role("button", name=name, exact=True).first.click()

    def go_to_dashboard(self):
        self._click_sidebar_link("Dashboard")
        self.wait_for_url("/dashboard")

    def go_to_merchant_list(self):
        self._click_sidebar_link("Merchants Lended")
        self.wait_for_url("/client-portal")

    def go_to_merchants_brokered(self):
        self._click_sidebar_link("Merchants Brokered")
        self.wait_for_url("/client-portal-brokered")

    def go_to_add_deal(self):
        self._click_sidebar_link("Add Deal")
        self.wait_for_url("/add-client")

    def go_to_add_brokered_deal(self):
        self._click_sidebar_link("Add Brokered Deal")
        self.wait_for_url("/add-brokered-deal")

    def go_to_reports(self):
        self._expand_sidebar_group("Reports")
        self._click_sidebar_link("In House")
        self.wait_for_url("/reports")

    def go_to_control_panel(self):
        self._expand_sidebar_group("Control Panel")
        self._click_sidebar_link("Overview")
        self.wait_for_url("/control-panel")

    def go_to_daily_payment_summary(self):
        self._click_sidebar_link("Daily Payment Summary")
        self.wait_for_url("/daily-payment-summary")
