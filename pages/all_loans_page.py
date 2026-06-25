"""
all_loans_page.py — All Loans page object (full client profile)
Tabs: Client Info, Businesses (Deals Info, Payment Info, Fees Info, Discounts, All), Statement, Change Logs
"""
import re
import allure
from playwright.sync_api import Page, expect
from pages.base_page import BasePage


class AllLoansPage(BasePage):
    # ── Top-level tabs ─────────────────────────────────────────────────────
    TAB_CLIENT_INFO  = "[data-testid='tab-client-info']"
    TAB_BUSINESSES   = "[data-testid='tab-businesses']"
    TAB_STATEMENT    = "[data-testid='tab-statement']"
    TAB_CHANGE_LOGS  = "[data-testid='tab-change-logs']"

    # ── Client Info fields ─────────────────────────────────────────────────
    CLIENT_FIRST_NAME = "[data-testid='client-first-name-display']"
    CLIENT_LAST_NAME  = "[data-testid='client-last-name-display']"
    CLIENT_EMAIL      = "[data-testid='client-email-display']"
    CLIENT_PROVINCE   = "[data-testid='client-province-display']"

    # ── Business / Deal deal sub-tabs ──────────────────────────────────────
    FUND_DEAL_BTN     = "[data-testid='fund-deal-btn']"
    DEAL_STATUS_BADGE = "[data-testid='deal-status-badge']"

    SUB_TAB_DEALS_INFO    = "[data-testid='subtab-deals-info']"
    SUB_TAB_PAYMENT_INFO  = "[data-testid='subtab-payment-info']"
    SUB_TAB_FEES_INFO     = "[data-testid='subtab-fees-info']"
    SUB_TAB_DISCOUNTS     = "[data-testid='subtab-discounts']"
    SUB_TAB_ALL           = "[data-testid='subtab-all']"

    # ── Deals Info values ──────────────────────────────────────────────────
    DI_FUNDING_AMOUNT    = "[data-testid='di-funding-amount']"
    DI_FACTOR_RATE       = "[data-testid='di-factor-rate']"
    DI_COST_BORROWING    = "[data-testid='di-cost-of-borrowing']"
    DI_TOTAL_PAYABLE     = "[data-testid='di-total-payable']"
    DI_AMOUNT_CREDITED   = "[data-testid='di-amount-credited']"
    DI_PAD_FEE           = "[data-testid='di-pad-fee']"
    DI_UW_FEE            = "[data-testid='di-uw-fee']"
    DI_START_DATE        = "[data-testid='di-start-date']"
    DI_END_DATE          = "[data-testid='di-end-date']"
    DI_PAYMENT_FREQ      = "[data-testid='di-payment-frequency']"
    DI_NUM_PAYMENTS      = "[data-testid='di-num-payments']"
    DI_RENEWAL_ELIGIBLE  = "[data-testid='di-renewal-eligible']"

    # ── Payment Info values ────────────────────────────────────────────────
    PI_PAYMENT_AMOUNT    = "[data-testid='pi-payment-amount']"
    PI_TOTAL_PAYMENTS    = "[data-testid='pi-total-payments']"
    PI_AMOUNT_COLLECTED  = "[data-testid='pi-amount-collected']"
    PI_BALANCE           = "[data-testid='pi-balance']"
    PI_TOTAL_PAYABLE_FEE = "[data-testid='pi-total-payable-with-fees']"
    PI_TOTAL_BALANCE     = "[data-testid='pi-total-balance']"
    PI_ADVANCE_PCT       = "[data-testid='pi-advance-collected-pct']"
    PI_NSF_COUNT         = "[data-testid='pi-nsf-count']"

    # ── Fees Info values ───────────────────────────────────────────────────
    FI_NSF_TOTAL         = "[data-testid='fi-nsf-fee-total']"
    FI_NSF_PAID          = "[data-testid='fi-nsf-paid']"
    FI_NSF_OUTSTANDING   = "[data-testid='fi-nsf-outstanding']"
    FI_DELAY_TOTAL       = "[data-testid='fi-delay-fee-total']"
    FI_LEGAL_TOTAL       = "[data-testid='fi-legal-fee-total']"
    FI_TOTAL_FEE         = "[data-testid='fi-total-fee']"

    # ── Fund Deal modal ────────────────────────────────────────────────────
    MODAL_COST_BORROWING  = "[data-testid='modal-cost-of-borrowing']"
    MODAL_TOTAL_PAYABLE   = "[data-testid='modal-total-payable']"
    MODAL_AMOUNT_CREDITED = "[data-testid='modal-amount-credited']"
    MODAL_PAYMENT_AMOUNT  = "[data-testid='modal-payment-amount']"
    MODAL_CONFIRM_BTN     = "[data-testid='fund-deal-confirm-btn']"
    MODAL_CANCEL_BTN      = "[data-testid='fund-deal-cancel-btn']"

    def __init__(self, page: Page):
        super().__init__(page)

    @allure.step("Click Fund Deal button")
    def click_fund_deal(self):
        self.click(self.FUND_DEAL_BTN)
        self.wait_for_selector(self.MODAL_CONFIRM_BTN)

    @allure.step("Read Fund Deal modal values")
    def get_modal_values(self) -> dict:
        return {
            "cost_of_borrowing": self._parse_amount(self.MODAL_COST_BORROWING),
            "total_payable":     self._parse_amount(self.MODAL_TOTAL_PAYABLE),
            "amount_credited":   self._parse_amount(self.MODAL_AMOUNT_CREDITED),
            "payment_amount":    self._parse_amount(self.MODAL_PAYMENT_AMOUNT),
        }

    @allure.step("Confirm Fund Deal")
    def confirm_fund_deal(self):
        self.click(self.MODAL_CONFIRM_BTN)
        self.wait_for_network_idle()

    @allure.step("Read Deals Info tab values")
    def get_deals_info(self) -> dict:
        self.click(self.SUB_TAB_DEALS_INFO)
        return {
            "funding_amount":  self._parse_amount(self.DI_FUNDING_AMOUNT),
            "factor_rate":     float(self.page.locator(self.DI_FACTOR_RATE).inner_text()),
            "cost_borrowing":  self._parse_amount(self.DI_COST_BORROWING),
            "total_payable":   self._parse_amount(self.DI_TOTAL_PAYABLE),
            "amount_credited": self._parse_amount(self.DI_AMOUNT_CREDITED),
            "pad_fee":         self._parse_amount(self.DI_PAD_FEE),
            "uw_fee":          self._parse_amount(self.DI_UW_FEE),
            "start_date":      self.page.locator(self.DI_START_DATE).inner_text().strip(),
            "payment_freq":    self.page.locator(self.DI_PAYMENT_FREQ).inner_text().strip(),
        }

    @allure.step("Read Payment Info tab values")
    def get_payment_info(self) -> dict:
        self.click(self.SUB_TAB_PAYMENT_INFO)
        return {
            "payment_amount":    self._parse_amount(self.PI_PAYMENT_AMOUNT),
            "amount_collected":  self._parse_amount(self.PI_AMOUNT_COLLECTED),
            "balance":           self._parse_amount(self.PI_BALANCE),
            "total_payable_fee": self._parse_amount(self.PI_TOTAL_PAYABLE_FEE),
            "total_balance":     self._parse_amount(self.PI_TOTAL_BALANCE),
            "advance_pct":       self._parse_pct(self.PI_ADVANCE_PCT),
            "nsf_count":         int(self.page.locator(self.PI_NSF_COUNT).inner_text() or "0"),
        }

    @allure.step("Read Fees Info tab values")
    def get_fees_info(self) -> dict:
        self.click(self.SUB_TAB_FEES_INFO)
        return {
            "nsf_total":       self._parse_amount(self.FI_NSF_TOTAL),
            "nsf_paid":        self._parse_amount(self.FI_NSF_PAID),
            "nsf_outstanding": self._parse_amount(self.FI_NSF_OUTSTANDING),
            "delay_total":     self._parse_amount(self.FI_DELAY_TOTAL),
            "legal_total":     self._parse_amount(self.FI_LEGAL_TOTAL),
            "total_fee":       self._parse_amount(self.FI_TOTAL_FEE),
        }

    @allure.step("Get deal status badge text")
    def get_deal_status(self) -> str:
        return self.page.locator(self.DEAL_STATUS_BADGE).first.inner_text().strip()

    # ── Internal helpers ───────────────────────────────────────────────────
    def _parse_amount(self, selector: str) -> float:
        """Strip currency symbols and parse to float."""
        raw = self.page.locator(selector).inner_text()
        cleaned = re.sub(r"[^\d.]", "", raw)
        return float(cleaned) if cleaned else 0.0

    def _parse_pct(self, selector: str) -> float:
        raw = self.page.locator(selector).inner_text()
        cleaned = re.sub(r"[^\d.]", "", raw)
        return float(cleaned) if cleaned else 0.0
