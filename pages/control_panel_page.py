"""
control_panel_page.py — Control Panel page object (live KESEF QA)

The Control Panel is a tabbed page (MUI tabs, UPPERCASE labels):
  LEAD SOURCES | BROKERAGES | SALES REPS | ISO MANAGERS | HOLIDAYS |
  INSTITUTIONS | UNDERWRITERS | PROVINCES | INDUSTRIES | LENDERS | ASSISTS |
  USER MANAGEMENT | PAYMENT DECLINED | PAYMENT PROCESSOR

Each tab shows a table (Name | Active Status | Added On | Updated On | Action)
and an "Add <Section>" button that opens a small modal with a floating-label
field and Cancel / Add buttons. There are no custom data-testids.
"""
import allure
from playwright.sync_api import Page, expect
from pages.base_page import BasePage

DEFAULT_TIMEOUT = 10_000


class ControlPanelPage(BasePage):
    # Tab labels (as rendered, uppercase)
    TAB_LEAD_SOURCES = "LEAD SOURCES"
    TAB_SALES_REPS   = "SALES REPS"
    TAB_HOLIDAYS     = "HOLIDAYS"
    TAB_UNDERWRITERS = "UNDERWRITERS"

    def __init__(self, page: Page):
        super().__init__(page)

    @allure.step("Go to Control Panel")
    def goto(self):
        self.page.goto("/control-panel")
        self.page.get_by_role("tab", name=self.TAB_LEAD_SOURCES).wait_for(
            state="visible", timeout=20_000)
        self.page.wait_for_timeout(800)

    # ── Internal helpers ─────────────────────────────────────────────────────
    def _open_tab(self, tab_name: str):
        self.page.get_by_role("tab", name=tab_name).first.click()
        self.page.wait_for_timeout(1000)

    def _click_add(self, add_button_name: str):
        self.page.get_by_role("button", name=add_button_name).first.click()
        self.page.wait_for_timeout(800)

    def _save_modal(self) -> str:
        """
        Click the modal's 'Add' button (exact, so it does not match 'Add Deal'),
        then capture the success snackbar text. Returns the toast text (or '').
        A successful add closes the modal and fires a '... added successfully'
        notistack snackbar; a rejected add (e.g. duplicate) leaves the modal open.
        """
        self.page.get_by_role("button", name="Add", exact=True).click()
        toast = ""
        for _ in range(16):
            self.page.wait_for_timeout(300)
            alert = self.page.locator("[role='alert'], .notistack-Snackbar")
            if alert.count():
                try:
                    toast = alert.first.inner_text().strip()
                    if toast:
                        break
                except Exception:
                    pass
        self.last_toast = toast
        return toast

    # ── Add operations ───────────────────────────────────────────────────────
    @allure.step("Add Lead Source: {name}")
    def add_lead_source(self, name: str):
        self._open_tab(self.TAB_LEAD_SOURCES)
        self._click_add("Add Lead Source")
        self.page.get_by_label("Lead Source Name").fill(name)
        self._save_modal()

    @allure.step("Add Sales Rep: {name}")
    def add_sales_rep(self, name: str, email: str, phone: str = "9990001234"):
        self._open_tab(self.TAB_SALES_REPS)
        self._click_add("Add Sales Rep")
        self.page.locator("input[name='name']").fill(name)
        self.page.locator("input[name='phone']").fill(phone)
        self.page.locator("input[name='email']").fill(email)
        self._save_modal()

    @allure.step("Add Holiday: {date} ({description})")
    def add_holiday(self, date: str, description: str):
        """`date` must be in MM/DD/YYYY format (the field's mask)."""
        self._open_tab(self.TAB_HOLIDAYS)
        self._click_add("Add Holiday")
        picker = self.page.get_by_label("Pick a date", exact=True)
        picker.click()
        picker.press("Control+a")
        picker.type(date.replace("-", "/"))
        self.page.locator("input[name='holiday']").fill(description)
        self._save_modal()

    # ── Verification ─────────────────────────────────────────────────────────
    @allure.step("Get all Name-column values in the current tab")
    def get_all_items(self) -> list[str]:
        cells = self.page.locator("table tbody tr td:nth-child(2)")
        return [cells.nth(i).inner_text().strip() for i in range(cells.count())]

    @allure.step("Assert the last add succeeded")
    def assert_add_succeeded(self):
        """
        A successful add fires a '... added successfully' snackbar and closes the
        modal. This is pagination-independent (the new row may sort onto a later
        page), so it is the reliable success check.
        """
        toast = (getattr(self, "last_toast", "") or "").lower()
        modal_open = self.page.get_by_role("button", name="Add", exact=True).count() > 0
        assert "success" in toast or not modal_open, (
            f"Add did not succeed — toast={self.last_toast!r}, modal still open={modal_open}"
        )

    @allure.step("Assert item exists in current tab: {name}")
    def assert_item_exists(self, name: str):
        expect(
            self.page.get_by_role("cell", name=name, exact=True).first
        ).to_be_visible(timeout=DEFAULT_TIMEOUT)
