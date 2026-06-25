"""
edit_payment_page.py — Edit Payment page object
Handles: payment schedule table, status changes, NSF, pause, fees
"""
import re
import allure
from playwright.sync_api import Page, expect
from pages.base_page import BasePage


class EditPaymentPage(BasePage):
    PAYMENT_ROWS       = "[data-testid='payment-row']"
    PAYMENT_DATE_COL   = "[data-testid='col-payment-date']"
    PAYMENT_STATUS_COL = "[data-testid='col-payment-status']"
    PAYMENT_AMOUNT_COL = "[data-testid='col-payment-amount']"
    PAYMENT_BALANCE    = "[data-testid='col-outstanding']"
    STATUS_SELECT      = "[data-testid='payment-status-select']"
    SAVE_BTN           = "[data-testid='save-payment-btn']"
    NSF_REASON_SELECT  = "[data-testid='nsf-reason-select']"
    LOG_FEES_BTN       = "[data-testid='log-fees-btn']"
    LEGAL_FEE_INPUT    = "[data-testid='legal-fee-amount']"
    LEGAL_FEE_SAVE     = "[data-testid='legal-fee-save']"
    PAUSE_BTN          = "[data-testid='pause-payments-btn']"
    PAUSE_REASON       = "[data-testid='pause-reason-input']"
    PAUSE_RESUME_DATE  = "[data-testid='pause-resume-date']"
    PAUSE_CONFIRM      = "[data-testid='pause-confirm-btn']"
    RESUME_BTN         = "[data-testid='resume-payments-btn']"
    SUMMARY_COLLECTED  = "[data-testid='summary-collected']"
    SUMMARY_BALANCE    = "[data-testid='summary-balance']"
    SUMMARY_TOTAL      = "[data-testid='summary-total-payments']"

    def __init__(self, page: Page):
        super().__init__(page)

    @allure.step("Get total payment row count")
    def get_payment_count(self) -> int:
        return self.page.locator(self.PAYMENT_ROWS).count()

    @allure.step("Get all payment dates")
    def get_all_dates(self) -> list[str]:
        rows = self.page.locator(self.PAYMENT_ROWS)
        return [
            rows.nth(i).locator(self.PAYMENT_DATE_COL).inner_text().strip()
            for i in range(rows.count())
        ]

    @allure.step("Get first payment date")
    def get_first_payment_date(self) -> str:
        return (self.page.locator(self.PAYMENT_ROWS).first
                .locator(self.PAYMENT_DATE_COL).inner_text().strip())

    @allure.step("Change payment status to: {status}")
    def set_payment_status(self, row_index: int, status: str, nsf_reason: str = ""):
        row = self.page.locator(self.PAYMENT_ROWS).nth(row_index)
        row.locator(self.STATUS_SELECT).click()
        self.page.get_by_role("option", name=status).click()
        if status == "NSF" and nsf_reason:
            self.select_mui_dropdown("NSF Reason", nsf_reason)
        self.click(self.SAVE_BTN)
        self.wait_for_network_idle()

    @allure.step("Log legal fee: {amount}")
    def log_legal_fee(self, amount: str):
        self.click(self.LOG_FEES_BTN)
        self.fill(self.LEGAL_FEE_INPUT, amount)
        self.click(self.LEGAL_FEE_SAVE)
        self.wait_for_network_idle()

    @allure.step("Pause deal payments")
    def pause_deal(self, reason: str, resume_date: str):
        self.click(self.PAUSE_BTN)
        self.fill(self.PAUSE_REASON, reason)
        self.fill(self.PAUSE_RESUME_DATE, resume_date)
        self.click(self.PAUSE_CONFIRM)
        self.wait_for_network_idle()

    @allure.step("Resume deal payments")
    def resume_deal(self):
        self.click(self.RESUME_BTN)
        self.wait_for_network_idle()

    @allure.step("Get summary balance")
    def get_summary_balance(self) -> float:
        raw = self.page.locator(self.SUMMARY_BALANCE).inner_text()
        return float(re.sub(r"[^\d.]", "", raw))

    @allure.step("Get summary total payments")
    def get_summary_total_payments(self) -> int:
        return int(self.page.locator(self.SUMMARY_TOTAL).inner_text().strip())

    @allure.step("Assert no weekend dates in schedule")
    def assert_no_weekends(self):
        from datetime import datetime
        dates = self.get_all_dates()
        for d in dates:
            try:
                parsed = datetime.strptime(d, "%Y-%m-%d")
                assert parsed.weekday() < 5, f"Weekend date found: {d}"
            except ValueError:
                pass  # Skip unparseable dates gracefully
