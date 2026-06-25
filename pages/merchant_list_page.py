"""
merchant_list_page.py — Merchant List / "Merchants Lended" (Client Portal) page object

Reflects the live KESEF QA app (no custom data-testids exist — only MUI icon testids):
  • Search box  : <input placeholder="Search Client">
  • Data grid   : the table whose header contains "Client Name". It renders rows
                  only after a search/filter; on first load it is empty and only a
                  "Summary of Filter/Searches" table is present.
  • Columns (0-indexed) of the Merchants Lended table:
        0 Serial No. | 1 Created Date | 2 Deal Status | 3 Client Name
        4 Legal Business Name | 5 Doing Business As | 6 Industry | 7 Province
        8 Deal No. | 9 Deal Type | 10 Date Funded | ... | 23 Amount Funded
  • No filter drawer exists; filtering is via the search box and column sorting.
"""
import re
import allure
from playwright.sync_api import Page, expect
from pages.base_page import BasePage


class MerchantListPage(BasePage):
    # ── Locators (real DOM) ──────────────────────────────────────────────────
    SEARCH_INPUT = "input[placeholder='Search Client']"
    # The Merchants Lended grid is the table whose header contains "Client Name".
    LENDED_TABLE = "//table[.//th[contains(normalize-space(.),'Client Name')]]"
    LENDED_ROWS  = "//table[.//th[contains(normalize-space(.),'Client Name')]]/tbody/tr"

    # Column indexes within a Merchants Lended row
    COL_SERIAL_NO     = 0
    COL_CREATED_DATE  = 1
    COL_DEAL_STATUS   = 2
    COL_CLIENT_NAME   = 3
    COL_BUSINESS_NAME = 4
    COL_DBA           = 5
    COL_INDUSTRY      = 6
    COL_PROVINCE      = 7
    COL_DEAL_NO       = 8
    COL_DEAL_TYPE     = 9
    COL_AMOUNT_FUNDED = 23

    def __init__(self, page: Page):
        super().__init__(page)

    # ── Navigation ───────────────────────────────────────────────────────────
    @allure.step("Go to Merchant List page")
    def goto(self):
        self.page.goto("/client-portal")
        self.page.wait_for_selector(self.SEARCH_INPUT, state="visible", timeout=20_000)

    # ── Search ───────────────────────────────────────────────────────────────
    @allure.step("Search for client: {name}")
    def search(self, name: str):
        box = self.page.locator(self.SEARCH_INPUT)
        box.click()
        box.fill(name)
        # Results load client-side after a short debounce; wait for at least one row
        # to appear (or settle if the query matches nothing).
        try:
            self.page.wait_for_selector(self.LENDED_ROWS, state="visible", timeout=8_000)
        except Exception:
            pass
        self.page.wait_for_timeout(1000)

    # ── Rows ─────────────────────────────────────────────────────────────────
    @allure.step("Get Merchants Lended row count")
    def get_row_count(self) -> int:
        return self.page.locator(self.LENDED_ROWS).count()

    def _row_for(self, client_name: str):
        return self.page.locator(self.LENDED_ROWS).filter(has_text=client_name).first

    @allure.step("Get row data for the first row matching: {client_name}")
    def get_deal_row_data(self, client_name: str) -> dict:
        cells = self._row_for(client_name).locator("td")
        return {
            "serial_no":     cells.nth(self.COL_SERIAL_NO).inner_text().strip(),
            "status":        cells.nth(self.COL_DEAL_STATUS).inner_text().strip(),
            "client_name":   cells.nth(self.COL_CLIENT_NAME).inner_text().strip(),
            "business_name": cells.nth(self.COL_BUSINESS_NAME).inner_text().strip(),
            "deal_no":       cells.nth(self.COL_DEAL_NO).inner_text().strip(),
            "deal_type":     cells.nth(self.COL_DEAL_TYPE).inner_text().strip(),
            "amount_funded": cells.nth(self.COL_AMOUNT_FUNDED).inner_text().strip(),
        }

    @allure.step("Get first row data")
    def get_first_row_data(self) -> dict:
        cells = self.page.locator(self.LENDED_ROWS).first.locator("td")
        return {
            "serial_no":     cells.nth(self.COL_SERIAL_NO).inner_text().strip(),
            "status":        cells.nth(self.COL_DEAL_STATUS).inner_text().strip(),
            "client_name":   cells.nth(self.COL_CLIENT_NAME).inner_text().strip(),
            "business_name": cells.nth(self.COL_BUSINESS_NAME).inner_text().strip(),
            "deal_no":       cells.nth(self.COL_DEAL_NO).inner_text().strip(),
            "deal_type":     cells.nth(self.COL_DEAL_TYPE).inner_text().strip(),
            "amount_funded": cells.nth(self.COL_AMOUNT_FUNDED).inner_text().strip(),
        }

    @allure.step("Assert client visible in list: {client_name}")
    def assert_client_visible(self, client_name: str):
        expect(self._row_for(client_name)).to_be_visible()

    # ── Financial values (for calculation verification) ──────────────────────
    @staticmethod
    def _num(text: str):
        cleaned = re.sub(r"[^\d.]", "", text or "")
        return float(cleaned) if cleaned else None

    def _header_index_map(self) -> dict:
        """Map each Merchants Lended header label -> its column index."""
        heads = self.page.locator(self.LENDED_TABLE + "//th")
        mapping = {}
        for i in range(heads.count()):
            name = heads.nth(i).inner_text().strip().split("\n")[0]
            if name and name not in mapping:
                mapping[name] = i
        return mapping

    @allure.step("Find a funded deal row and read its displayed financial values")
    def find_funded_deal(self) -> dict:
        """
        Search 'Test' and return the parsed financial columns of the first row
        that has a positive Amount Funded and Total Payback. Used to cross-check
        the app's displayed calculations against DealCalculator.
        """
        self.search("Test")
        idx = self._header_index_map()
        rows = self.page.locator(self.LENDED_ROWS)
        for i in range(min(rows.count(), 60)):
            cells = rows.nth(i).locator("td")
            funded  = self._num(cells.nth(idx["Amount Funded"]).inner_text())
            payback = self._num(cells.nth(idx["Total Payback"]).inner_text())
            if funded and funded > 0 and payback and payback > 0:
                def cell(name):
                    j = idx.get(name)
                    return cells.nth(j).inner_text().strip() if j is not None else ""
                return {
                    "status":          cell("Deal Status"),
                    "amount_funded":   funded,
                    "amount_credited": self._num(cell("Amount Credited")) or 0.0,
                    "total_payback":   payback,
                    "uw_fee":          self._num(cell("UW Fee")) or 0.0,
                    "pad_fee":         self._num(cell("PAD Fee")) or 0.0,
                    "buyout_amount":   self._num(cell("Buyout Amount")) or 0.0,
                    "factor_rate":     self._num(cell("Factor Rate")),
                    # Payment-schedule columns
                    "payment_amount":  self._num(cell("Daily/Weekly Payment Amount")) or 0.0,
                    "num_payments":    int(self._num(cell("Number of Payments")) or 0),
                    "payment_frequency": cell("Payment Frequency (Daily/Weekly)"),
                    "collected":       self._num(cell("Total Collected (Advance)")) or 0.0,
                    "outstanding":     self._num(cell("Total Outstanding (Advance)")) or 0.0,
                    "collected_pct":   self._num(cell("Total Collected % (Advance)")) or 0.0,
                    "nsf_count":       int(self._num(cell("Total NSF Count")) or 0),
                }
        raise AssertionError("No funded deal row (Amount Funded > 0) found under 'Test'")
