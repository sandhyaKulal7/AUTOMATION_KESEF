"""
reports_page.py — Reports page object (live KESEF QA)

The page has a single "Report type" MUI Select, a view toggle
(Analytical View / Both / Cashflow View), a "Time Period" preset, and an
"Export to Excel" button. The report renders automatically as a <table> when a
type is selected (there is no separate Generate button, and no from/to date
inputs). There is no drill-down modal.
"""
import re
import allure
from playwright.sync_api import Page, expect
from pages.base_page import BasePage

DEFAULT_TIMEOUT = 10_000


class ReportsPage(BasePage):
    REPORT_TYPE_SELECT = (
        "//label[contains(normalize-space(),'Report type')]"
        "/following::div[@role='combobox'][1]"
    )
    REPORT_ROWS = "table tbody tr"
    EXPORT_BTN  = "Export to Excel"

    def __init__(self, page: Page):
        super().__init__(page)

    @allure.step("Go to Reports page")
    def goto(self):
        self.page.goto("/reports")
        self.page.wait_for_selector(self.REPORT_TYPE_SELECT, state="visible", timeout=20_000)
        self.page.wait_for_timeout(1000)

    @allure.step("Select report type: {report_type}")
    def select_report_type(self, report_type: str):
        self.page.locator(self.REPORT_TYPE_SELECT).first.click()
        self.page.get_by_role("option", name=report_type, exact=True).click()
        self._wait_for_report()

    def _wait_for_report(self):
        """
        The report reloads on selection. The page keeps a long-lived connection
        open, so 'networkidle' never settles. Instead wait for the MUI skeleton
        loaders to disappear (data fetch complete), then for table rows.
        """
        self.page.wait_for_timeout(1000)
        try:
            self.page.wait_for_function(
                "() => document.querySelectorAll('.MuiSkeleton-root').length === 0",
                timeout=20_000,
            )
        except Exception:
            pass
        try:
            self.page.wait_for_selector(self.REPORT_ROWS, state="visible", timeout=10_000)
        except Exception:
            pass
        self.page.wait_for_timeout(1000)

    @allure.step("Get report row count")
    def get_row_count(self) -> int:
        return self.page.locator(self.REPORT_ROWS).count()

    @allure.step("Get report row data at index {index}")
    def get_row_data(self, index: int) -> dict:
        cells = self.page.locator(self.REPORT_ROWS).nth(index).locator("td")
        return {
            "label":         cells.nth(0).inner_text().strip(),
            "amount_funded": self._parse(cells.nth(1).inner_text() if cells.count() > 1 else ""),
        }

    @allure.step("Export report to Excel")
    def export_to_excel(self):
        """Click Export and return the triggered download object."""
        with self.page.expect_download(timeout=20_000) as dl_info:
            self.page.get_by_role("button", name=self.EXPORT_BTN).click()
        return dl_info.value

    @staticmethod
    def _parse(raw: str) -> float:
        cleaned = re.sub(r"[^\d.]", "", raw or "")
        return float(cleaned) if cleaned else 0.0
