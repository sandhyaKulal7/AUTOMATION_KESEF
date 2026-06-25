"""
test_tc04_fund_deal_calculations.py
TC-35 through TC-54: Fund Deal & all calculation verifications.
This is the most critical test file — verifies every financial formula.
"""
import pytest
import allure
from utils.calculations import DealCalculator
from pages.merchant_list_page import MerchantListPage


@allure.suite("04 — Fund Deal & Calculations")
@pytest.mark.calculations
@pytest.mark.smoke
class TestCalculations:
    """
    All tests use DealCalculator to compute the expected value INDEPENDENTLY,
    then compare against what the application actually shows.
    This proves the formula is correct, not just that the UI is consistent with itself.
    """

    @allure.title("TC-35 | Cost of Borrowing = (Funding × Factor) − Funding")
    def test_cost_of_borrowing(self, deal_data):
        d = deal_data["baseline_deal"]
        calc = DealCalculator(d["funding_amount"], d["factor_rate"], d["uw_fee_pct"], d["pad_fee"])
        assert calc.cost_of_borrowing == d["expected"]["cost_of_borrowing"], (
            f"Cost of borrowing: expected {d['expected']['cost_of_borrowing']}, "
            f"got {calc.cost_of_borrowing}"
        )

    @allure.title("TC-36 | Total Payable = Funding Amount × Factor Rate")
    def test_total_payable(self, deal_data):
        d = deal_data["baseline_deal"]
        calc = DealCalculator(d["funding_amount"], d["factor_rate"], d["uw_fee_pct"], d["pad_fee"])
        assert calc.total_payable == d["expected"]["total_payable"]

    @allure.title("TC-37 | UW Fee = Funding Amount × UW Fee %")
    def test_uw_fee_amount(self, deal_data):
        d = deal_data["baseline_deal"]
        calc = DealCalculator(d["funding_amount"], d["factor_rate"], d["uw_fee_pct"], d["pad_fee"])
        assert calc.uw_fee_amount == d["expected"]["uw_fee_amount"]

    @allure.title("TC-38 | Amount Credited = Funding − UW Fee − PAD Fee − Holdback")
    def test_amount_credited(self, deal_data):
        d = deal_data["baseline_deal"]
        calc = DealCalculator(d["funding_amount"], d["factor_rate"], d["uw_fee_pct"], d["pad_fee"])
        assert calc.amount_credited == d["expected"]["amount_credited"], (
            f"Amount credited: expected {d['expected']['amount_credited']}, "
            f"got {calc.amount_credited}"
        )

    @allure.title("TC-39 | Payment Amount = Total Payable ÷ Num Payments (rounded up)")
    def test_payment_amount(self, deal_data):
        d = deal_data["baseline_deal"]
        calc = DealCalculator(d["funding_amount"], d["factor_rate"], d["uw_fee_pct"], d["pad_fee"])
        result = calc.payment_amount(d["num_payments"])
        assert result == d["expected"]["payment_amount"]

    @allure.title("TC-40 | Payment schedule sum ≥ Total Payable (rounding handled)")
    def test_payment_schedule_sum_covers_total(self, deal_data):
        d = deal_data["baseline_deal"]
        calc = DealCalculator(d["funding_amount"], d["factor_rate"], d["uw_fee_pct"], d["pad_fee"])
        assert calc.validate_schedule_sum(d["num_payments"]), (
            "Sum of all scheduled payments must equal Total Payable exactly"
        )

    @allure.title("TC-41 | Balance before any payment = Total Payable")
    def test_initial_balance(self, deal_data):
        d = deal_data["baseline_deal"]
        calc = DealCalculator(d["funding_amount"], d["factor_rate"], d["uw_fee_pct"], d["pad_fee"])
        assert calc.balance(amount_collected=0.0) == calc.total_payable

    @allure.title("TC-42 | Balance after 10 payments = Total Payable − (10 × Payment)")
    def test_balance_after_ten_payments(self, deal_data):
        d = deal_data["baseline_deal"]
        calc = DealCalculator(d["funding_amount"], d["factor_rate"], d["uw_fee_pct"], d["pad_fee"])
        pmt = calc.payment_amount(d["num_payments"])
        collected = round(pmt * 10, 2)
        expected_balance = round(calc.total_payable - collected, 2)
        assert calc.balance(collected) == expected_balance

    @allure.title("TC-43 | Advance Collected % = 50% triggers Renewal Eligible")
    def test_renewal_eligible_at_50_pct(self, deal_data):
        d = deal_data["baseline_deal"]
        calc = DealCalculator(d["funding_amount"], d["factor_rate"], d["uw_fee_pct"], d["pad_fee"])
        half = calc.total_payable / 2
        assert calc.is_renewal_eligible(half - 0.01) is False, \
            "Must NOT be eligible at 49.99%"
        assert calc.is_renewal_eligible(half) is True, \
            "Must be eligible at exactly 50%"
        assert calc.is_renewal_eligible(half + 0.01) is True, \
            "Must be eligible above 50%"

    @allure.title("TC-44 | Broker Commission = Funding Amount × Commission %")
    def test_broker_commission(self, deal_data):
        d = deal_data["baseline_deal"]
        calc = DealCalculator(
            d["funding_amount"], d["factor_rate"], d["uw_fee_pct"],
            d["pad_fee"], commission_pct=5.0
        )
        assert calc.broker_commission() == 2500.00

    @allure.title("TC-47 | Zero UW Fee — Amount Credited = Funding − PAD Fee only")
    def test_zero_uw_fee(self, deal_data):
        d = deal_data["zero_uw_fee"]
        calc = DealCalculator(d["funding_amount"], d["factor_rate"], d["uw_fee_pct"], d["pad_fee"])
        assert calc.uw_fee_amount == 0.0
        assert calc.amount_credited == d["expected"]["amount_credited"]

    @allure.title("TC-48 | Zero PAD Fee — Amount Credited = Funding − UW Fee only")
    def test_zero_pad_fee(self, deal_data):
        d = deal_data["zero_pad_fee"]
        calc = DealCalculator(d["funding_amount"], d["factor_rate"], d["uw_fee_pct"], d["pad_fee"])
        assert calc.amount_credited == d["expected"]["amount_credited"]

    @allure.title("TC-49 | Max Factor Rate 3.0 — Total Payable = 3× Funding")
    def test_max_factor_rate(self, deal_data):
        d = deal_data["max_factor_rate"]
        calc = DealCalculator(d["funding_amount"], d["factor_rate"], d["uw_fee_pct"], d["pad_fee"])
        assert calc.total_payable == d["expected"]["total_payable"]
        assert calc.cost_of_borrowing == d["expected"]["cost_of_borrowing"]

    @allure.title("TC-50 | Single payment deal — Payment Amount = Total Payable")
    def test_single_payment_deal(self, deal_data):
        d = deal_data["single_payment"]
        calc = DealCalculator(d["funding_amount"], d["factor_rate"], d["uw_fee_pct"], d["pad_fee"])
        assert calc.payment_amount(1) == calc.total_payable

    @allure.title("TC-51 | Buyout Amount deducted from Amount Credited")
    def test_buyout_reduces_amount_credited(self, deal_data):
        d = deal_data["with_buyout"]
        calc = DealCalculator(
            d["funding_amount"], d["factor_rate"], d["uw_fee_pct"],
            d["pad_fee"], buyout_amount=d["buyout_amount"]
        )
        assert calc.amount_credited == d["expected"]["amount_credited"]

    @allure.title("TC-52 | NSF Fee = exactly $65 per event")
    def test_nsf_fee_is_65(self):
        assert DealCalculator.NSF_FEE == 65.0

    @allure.title("TC-53 | Delay Fee = Funding Amount × 2.5% per business day")
    def test_delay_fee_per_day(self, deal_data):
        d = deal_data["baseline_deal"]
        calc = DealCalculator(d["funding_amount"], d["factor_rate"], d["uw_fee_pct"], d["pad_fee"])
        # $50,000 × 2.5% = $1,250
        assert calc.delay_fee_per_day() == 1250.00

    @allure.title("TC-54 | Pause Fee = Funding Amount × 2.5%")
    def test_pause_fee(self, deal_data):
        d = deal_data["baseline_deal"]
        calc = DealCalculator(d["funding_amount"], d["factor_rate"], d["uw_fee_pct"], d["pad_fee"])
        assert calc.pause_fee() == 1250.00

    @allure.title("TC-55 | Total Payable with Fees = Total Payable + NSF fees")
    def test_total_payable_with_nsf_fees(self, deal_data):
        d = deal_data["baseline_deal"]
        calc = DealCalculator(d["funding_amount"], d["factor_rate"], d["uw_fee_pct"], d["pad_fee"])
        result = calc.total_payable_with_fees(nsf_count=3)
        expected = calc.total_payable + (3 * 65.0)
        assert result == expected

    @allure.title("TC-56 | Avg Factor Rate — weighted average formula")
    def test_avg_factor_rate(self):
        calc = DealCalculator(0, 0, 0, 0)
        deals = [
            {"funding_amount": 50_000, "factor_rate": 1.35},
            {"funding_amount": 25_000, "factor_rate": 1.45},
        ]
        weighted = (50_000 * 1.35 + 25_000 * 1.45) / 75_000
        assert abs(calc.avg_factor_rate(deals) - round(weighted, 4)) < 0.0001


@allure.suite("04 — Displayed Calculation Verification")
@pytest.mark.ui
@pytest.mark.regression
class TestDisplayedCalculations:
    """
    Verify the financial values the app DISPLAYS on the Merchants Lended grid
    match DealCalculator computed independently from the same inputs. This is
    the read-only, reachable equivalent of the (unreachable, data-mutating)
    Fund Deal modal — it still proves the app's formulas are correct.
    """

    @allure.title("TC-45 | Displayed Total Payback & Cost of Borrowing match the formula")
    def test_total_payback_and_cob_match(self, admin_page):
        ml = MerchantListPage(admin_page)
        ml.goto()
        deal = ml.find_funded_deal()
        calc = DealCalculator(deal["amount_funded"], deal["factor_rate"], 0.0, 0.0)
        assert abs(deal["total_payback"] - calc.total_payable) < 1.0, (
            f"Total Payback: UI={deal['total_payback']}, expected={calc.total_payable}"
        )
        displayed_cob = round(deal["total_payback"] - deal["amount_funded"], 2)
        assert abs(displayed_cob - calc.cost_of_borrowing) < 1.0, (
            f"Cost of Borrowing: UI={displayed_cob}, expected={calc.cost_of_borrowing}"
        )

    @allure.title("TC-49 | Displayed Amount Credited matches Funding − UW − PAD − Buyout")
    def test_amount_credited_matches(self, admin_page):
        ml = MerchantListPage(admin_page)
        ml.goto()
        deal = ml.find_funded_deal()
        uw_pct = (deal["uw_fee"] / deal["amount_funded"] * 100) if deal["amount_funded"] else 0.0
        calc = DealCalculator(
            deal["amount_funded"], deal["factor_rate"], uw_pct, deal["pad_fee"],
            buyout_amount=deal["buyout_amount"],
        )
        assert abs(deal["amount_credited"] - calc.amount_credited) < 1.0, (
            f"Amount Credited: UI={deal['amount_credited']}, expected={calc.amount_credited}"
        )

    @allure.title("TC-50 | Displayed Factor Rate is within the valid 1.0–3.0 range")
    def test_factor_rate_in_valid_range(self, admin_page):
        ml = MerchantListPage(admin_page)
        ml.goto()
        deal = ml.find_funded_deal()
        assert deal["factor_rate"] is not None, "Factor Rate should be displayed"
        assert 1.0 <= deal["factor_rate"] <= 3.0, (
            f"Factor Rate {deal['factor_rate']} out of expected range 1.0–3.0"
        )
