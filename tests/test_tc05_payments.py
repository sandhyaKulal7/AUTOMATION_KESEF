"""
test_tc05_payments.py — Payment schedule, balances & NSF (displayed-value verification)

The Edit Payment / payment-schedule screen is not reachable (the Merchants
Lended grid does not navigate to a loan detail), and changing a payment status
(NSF / Approved) would irreversibly mutate live QA data. Instead these tests
verify the payment-engine values the app DISPLAYS on the Merchants Lended grid
against the same formulas in DealCalculator — read-only and side-effect free.
The pure NSF / balance / schedule math is covered in test_tc04 TestCalculations.
"""
import math
import pytest
import allure
from pages.merchant_list_page import MerchantListPage


@allure.suite("05 — Payment schedule values")
@pytest.mark.payments
@pytest.mark.regression
class TestPaymentSchedule:

    @allure.title("TC-57 | Displayed Payment Amount = ceil(Total Payback ÷ Number of Payments)")
    def test_payment_amount_matches_formula(self, admin_page):
        ml = MerchantListPage(admin_page)
        ml.goto()
        deal = ml.find_funded_deal()
        assert deal["num_payments"] >= 1, "Number of Payments should be a positive integer"
        expected = math.ceil(deal["total_payback"] / deal["num_payments"] * 100) / 100
        # Grid shows the payment amount rounded to whole dollars; allow $1 tolerance.
        assert abs(deal["payment_amount"] - expected) < 1.5, (
            f"Payment Amount: UI={deal['payment_amount']}, expected≈{expected}"
        )

    @allure.title("TC-58 | Payment Frequency is Daily or Weekly")
    def test_payment_frequency_valid(self, admin_page):
        ml = MerchantListPage(admin_page)
        ml.goto()
        deal = ml.find_funded_deal()
        assert deal["payment_frequency"].lower() in ("daily", "weekly"), (
            f"Unexpected payment frequency: {deal['payment_frequency']!r}"
        )

    @allure.title("TC-60 | Outstanding (Advance) = Total Payback − Total Collected")
    def test_outstanding_equals_payback_minus_collected(self, admin_page):
        ml = MerchantListPage(admin_page)
        ml.goto()
        deal = ml.find_funded_deal()
        expected = round(deal["total_payback"] - deal["collected"], 2)
        assert abs(deal["outstanding"] - expected) < 1.0, (
            f"Outstanding: UI={deal['outstanding']}, expected={expected}"
        )


@allure.suite("05 — NSF & collection values")
@pytest.mark.payments
@pytest.mark.regression
class TestNSFEvents:

    @allure.title("TC-65 | NSF Count is a valid non-negative integer")
    def test_nsf_count_is_valid(self, admin_page):
        ml = MerchantListPage(admin_page)
        ml.goto()
        deal = ml.find_funded_deal()
        assert isinstance(deal["nsf_count"], int) and deal["nsf_count"] >= 0, (
            f"NSF Count should be a non-negative integer, got {deal['nsf_count']}"
        )


@allure.suite("05 — Collection percentage")
@pytest.mark.payments
@pytest.mark.regression
class TestPaymentApproval:

    @allure.title("TC-63 | Total Collected % = Total Collected ÷ Total Payback × 100")
    def test_collected_pct_matches_ratio(self, admin_page):
        ml = MerchantListPage(admin_page)
        ml.goto()
        deal = ml.find_funded_deal()
        expected_pct = round(deal["collected"] / deal["total_payback"] * 100, 2) \
            if deal["total_payback"] else 0.0
        assert abs(deal["collected_pct"] - expected_pct) < 1.0, (
            f"Collected %: UI={deal['collected_pct']}, expected≈{expected_pct}"
        )
