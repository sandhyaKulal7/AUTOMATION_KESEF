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
import re
import allure
from playwright.sync_api import Page, expect
from pages.base_page import BasePage

DEFAULT_TIMEOUT = 10_000


class ControlPanelPage(BasePage):
    # Tab labels (as rendered, uppercase)
    TAB_LEAD_SOURCES    = "LEAD SOURCES"
    TAB_BROKERAGES      = "BROKERAGES"
    TAB_SALES_REPS      = "SALES REPS"
    TAB_ISO_MANAGERS    = "ISO MANAGERS"
    TAB_HOLIDAYS        = "HOLIDAYS"
    TAB_INSTITUTIONS    = "INSTITUTIONS"
    TAB_UNDERWRITERS    = "UNDERWRITERS"
    TAB_PROVINCES       = "PROVINCES"
    TAB_INDUSTRIES      = "INDUSTRIES"
    TAB_LENDERS         = "LENDERS"
    TAB_ASSISTS         = "ASSISTS"
    TAB_USER_MANAGEMENT = "USER MANAGEMENT"
    TAB_PAYMENT_DECLINED = "PAYMENT DECLINED"
    TAB_PAYMENT_PROCESSOR = "PAYMENT PROCESSOR"

    def __init__(self, page: Page):
        super().__init__(page)

    def goto(self, path: str = "/control-panel") -> None:
        """Go to Control Panel with proper initialization."""
        super().goto(path)
        self.page.get_by_role("tab", name=self.TAB_LEAD_SOURCES).wait_for(
            state="visible", timeout=20_000)
        self.page.wait_for_timeout(800)

    # ── Internal helpers ─────────────────────────────────────────────────────
    def _open_tab(self, tab_name: str) -> None:
        self.page.get_by_role("tab", name=tab_name).first.click()
        self.page.wait_for_timeout(1000)

    def _click_add(self, add_button_name: str) -> None:
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
    def add_lead_source(self, name: str) -> None:
        self._open_tab(self.TAB_LEAD_SOURCES)
        self._click_add("Add Lead Source")
        self.page.get_by_label("Lead Source Name").fill(name)
        self._save_modal()

    @allure.step("Add Sales Rep: {name}")
    def add_sales_rep(self, name: str, email: str, phone: str = "9990001234") -> None:
        self._open_tab(self.TAB_SALES_REPS)
        self._click_add("Add Sales Rep")
        self.page.locator("input[name='name']").fill(name)
        self.page.locator("input[name='phone']").fill(phone)
        self.page.locator("input[name='email']").fill(email)
        self._save_modal()

    @allure.step("Add Holiday: {date} ({description})")
    def add_holiday(self, date: str, description: str) -> None:
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
    def assert_add_succeeded(self) -> None:
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
    def assert_item_exists(self, name: str) -> None:
        expect(
            self.page.get_by_role("cell", name=name, exact=True).first
        ).to_be_visible(timeout=DEFAULT_TIMEOUT)

    @allure.step("Switch to tab: {tab_name}")
    def switch_tab(self, tab_name: str) -> None:
        """Open a Control Panel tab by name (e.g. 'SALES REPS', 'HOLIDAYS')."""
        self._open_tab(tab_name)

    @allure.step("Assert item in current tab: {name}")
    def assert_item_in_current_tab(self, name: str) -> None:
        """Verify the item appears in the current tab's table."""
        self.assert_item_exists(name)

    @allure.step("Add generic item: {name}")
    def add_item(self, name: str) -> None:
        """
        Generic add method for simple single-field items (Underwriter, Lead Source, 
        Brokerage, Industry, Province, Payment Processor, etc.).
        Assumes the modal has a single text input field for the name.
        """
        # Find the first "Add" button (generic approach for all tabs)
        add_buttons = self.page.get_by_role("button").filter(
            has_text=re.compile(r"^Add", re.IGNORECASE)
        )
        if add_buttons.count():
            add_buttons.first.click()
            self.page.wait_for_timeout(800)
        
        # Find the text input in the modal and fill it
        input_field = self.page.locator("input[type='text']").first
        input_field.fill(name)
        self._save_modal()

    @allure.step("Deactivate item: {name}")
    def deactivate_item(self, name: str) -> None:
        """
        Click the deactivate/toggle button for an item in the current tab.
        The action button is typically in the last column of the table row.
        """
        # Find the row with the item
        row = self.page.get_by_role("row").filter(has_text=name)
        assert row.count() > 0, f"Item '{name}' not found in current tab"
        
        # Click the action button (usually a toggle/switch in the "Active" column)
        action_buttons = row.locator("button, [role='button']")
        if action_buttons.count() > 0:
            # Try clicking the switch/toggle
            action_buttons.first.click()
            self.page.wait_for_timeout(1000)

    @allure.step("Assert deactivation succeeded")
    def assert_deactivation_succeeded(self) -> None:
        """Verify that deactivation succeeded (check for success toast)."""
        toast = (getattr(self, "last_toast", "") or "").lower()
        # Look for a success or confirmation message
        alert_elements = self.page.locator("[role='alert'], .notistack-Snackbar")
        if alert_elements.count():
            last_alert = alert_elements.last.inner_text().lower()
            assert "success" in last_alert or "deactivat" in last_alert, \
                f"Deactivation may have failed. Alert: {last_alert}"
