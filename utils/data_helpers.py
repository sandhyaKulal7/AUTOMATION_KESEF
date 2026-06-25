"""
data_helpers.py — Test data factories using Faker.
Generates randomised data so tests never collide when run in parallel.
"""
from faker import Faker
from datetime import date, timedelta

fake = Faker("en_CA")


class DealDataFactory:
    @staticmethod
    def new_client_payload(
        funding_amount: float = 50_000.0,
        factor_rate: float = 1.35,
        uw_fee_pct: float = 3.0,
        pad_fee: float = 100.0,
        num_payments: int = 125,
        frequency: str = "Daily",
    ) -> dict:
        start_date = DealDataFactory._next_business_day()
        return {
            "first_name":    fake.first_name(),
            "last_name":     fake.last_name(),
            "email":         fake.unique.email(),
            "phone":         fake.numerify("416-###-####"),
            "province":      "Ontario",
            "legal_name":    fake.company(),
            "industry":      "Restaurant",
            "biz_province":  "Ontario",
            "sales_rep":     "Test Sales Rep",
            "lead_source":   "Test Lead Source",
            "funding_amount": str(int(funding_amount)),
            "factor_rate":    str(factor_rate),
            "uw_fee_pct":     str(uw_fee_pct),
            "pad_fee":        str(int(pad_fee)),
            "holdback":       "0",
            "frequency":      frequency,
            "start_date":     start_date,
            "num_payments":   str(num_payments),
            "underwriter":   "Test Underwriter",
        }

    @staticmethod
    def _next_business_day() -> str:
        d = date.today() + timedelta(days=1)
        while d.weekday() >= 5:   # 5=Sat, 6=Sun
            d += timedelta(days=1)
        return d.strftime("%Y-%m-%d")
