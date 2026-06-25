"""
calculations.py — Pure Python mirrors of the KESEF calculation engine.
Used by test assertions to compute expected values independently of the UI.
No Playwright code here — this is a pure calculation library.
"""
import math


class DealCalculator:
    """
    Mirrors CalculationServiceImpl.kt exactly.
    Use this to derive expected values and compare against what the UI shows.
    """
    # Constants from AppConstant.kt
    NSF_FEE            = 65.0
    DELAY_FEE_PCT      = 2.5      # percent per business day
    PAUSE_FEE_PCT      = 2.5      # percent (one-time per pause)
    RENEWAL_THRESHOLD  = 50.0     # percent

    def __init__(
        self,
        funding_amount: float,
        factor_rate: float,
        uw_fee_pct: float,
        pad_fee: float,
        additional_holdback: float = 0.0,
        buyout_amount: float = 0.0,
        commission_pct: float = 0.0,
    ):
        self.funding_amount       = funding_amount
        self.factor_rate          = factor_rate
        self.uw_fee_pct           = uw_fee_pct
        self.pad_fee              = pad_fee
        self.additional_holdback  = additional_holdback
        self.buyout_amount        = buyout_amount
        self.commission_pct       = commission_pct

    # ── Core calculated fields ─────────────────────────────────────────────

    @property
    def cost_of_borrowing(self) -> float:
        """(Funding Amount × Factor Rate) − Funding Amount"""
        return round((self.funding_amount * self.factor_rate) - self.funding_amount, 2)

    @property
    def total_payable(self) -> float:
        """Funding Amount × Factor Rate"""
        return round(self.funding_amount * self.factor_rate, 2)

    @property
    def uw_fee_amount(self) -> float:
        """Funding Amount × UW Fee %"""
        return round(self.funding_amount * self.uw_fee_pct / 100, 2)

    @property
    def amount_credited(self) -> float:
        """Funding Amount − UW Fee − PAD Fee − Additional Holdback − Buyout Amount"""
        return round(
            self.funding_amount
            - self.uw_fee_amount
            - self.pad_fee
            - self.additional_holdback
            - self.buyout_amount,
            2,
        )

    def payment_amount(self, num_payments: int) -> float:
        """Total Payable ÷ Number of Payments (rounded UP to cent)"""
        raw = self.total_payable / num_payments
        return math.ceil(raw * 100) / 100

    def num_payments_from_payment_amount(self, payment_amount: float) -> int:
        """Total Payable ÷ Payment Amount (rounded UP)"""
        return math.ceil(self.total_payable / payment_amount)

    def broker_commission(self) -> float:
        """Funding Amount × Commission %"""
        return round(self.funding_amount * self.commission_pct / 100, 2)

    # ── Running calculations ───────────────────────────────────────────────

    def balance(self, amount_collected: float, discounts: float = 0.0) -> float:
        """Total Payable − Amount Collected − Discounts"""
        return round(self.total_payable - amount_collected - discounts, 2)

    def advance_collected_pct(self, amount_collected: float) -> float:
        """(Amount Collected ÷ Total Payable) × 100"""
        return round((amount_collected / self.total_payable) * 100, 2)

    def is_renewal_eligible(self, amount_collected: float) -> bool:
        """
        True when Advance Collected % ≥ 50%.
        Uses raw ratio (not rounded %) to avoid false positives —
        e.g. $33,749.99 on $67,500 = 49.9999...% rounds to 50.00% but must NOT pass.
        """
        raw_pct = (amount_collected / self.total_payable) * 100
        return raw_pct >= self.RENEWAL_THRESHOLD

    def total_payable_with_fees(
        self, nsf_count: int = 0, delay_fee: float = 0.0, legal_fee: float = 0.0
    ) -> float:
        """Total Payable + All accumulated fees"""
        nsf_total = nsf_count * self.NSF_FEE
        return round(self.total_payable + nsf_total + delay_fee + legal_fee, 2)

    def delay_fee_per_day(self) -> float:
        """Funding Amount × 2.5% per business day past end date"""
        return math.ceil(self.funding_amount * self.DELAY_FEE_PCT / 100 * 100) / 100

    def pause_fee(self) -> float:
        """Funding Amount × 2.5% (one-time per pause period)"""
        return round(self.funding_amount * self.PAUSE_FEE_PCT / 100, 2)

    # ── Validation helpers ─────────────────────────────────────────────────

    def payment_schedule_sum(self, num_payments: int) -> float:
        """
        Sum of all payments = (num_payments - 1) × standard amount + last_payment
        Last payment = Total Payable − sum of prior payments
        """
        pmt = self.payment_amount(num_payments)
        prior_sum = round(pmt * (num_payments - 1), 2)
        last_payment = round(self.total_payable - prior_sum, 2)
        return round(prior_sum + last_payment, 2)

    def validate_schedule_sum(self, num_payments: int) -> bool:
        """Sum of all scheduled payments must equal Total Payable exactly."""
        return abs(self.payment_schedule_sum(num_payments) - self.total_payable) < 0.01

    def avg_factor_rate(self, deals: list[dict]) -> float:
        """
        Weighted average factor rate across multiple deals.
        deals: list of {"funding_amount": float, "factor_rate": float}
        """
        total_funded = sum(d["funding_amount"] for d in deals)
        if total_funded == 0:
            return 0.0
        weighted_sum = sum(d["funding_amount"] * d["factor_rate"] for d in deals)
        return round(weighted_sum / total_funded, 4)
