"""
test_tc06_pause_resume.py — Pause & Resume (read-only verification)

Pausing/resuming a deal is a destructive state transition performed on the
Edit Payment screen, which is not reachable (the Merchants Lended grid does not
navigate to a loan detail) and would irreversibly mutate live QA data (status
change + a one-time pause fee). So instead of driving that workflow, these tests
verify the observable facts it depends on:
  • the Deal Status enum the pause/resume feature transitions between, and
  • the Pause Fee rule (Funding × 2.5%) applied to a real deal's funding amount.
The pure pause-fee math is also covered in test_tc04 TestCalculations.
"""
import pytest
import allure
from pages.merchant_list_page import MerchantListPage
from utils.calculations import DealCalculator

# Deal statuses the app is expected to use (pause/resume toggles ACTIVE ↔ PAUSED).
ALLOWED_STATUSES = {
    "active", "ready", "completed", "paused", "active paused",
    "cancelled", "canceled", "declined", "closed", "defaulted", "renewed",
}


@allure.suite("06 — Pause & Resume")
@pytest.mark.payments
@pytest.mark.regression
class TestPauseResume:

    @allure.title("TC-76 | Deal Status values are within the valid status set")
    def test_deal_status_values_valid(self, admin_page):
        ml = MerchantListPage(admin_page)
        ml.goto()
        ml.search("Test")
        idx = ml._header_index_map()
        rows = ml.page.locator(ml.LENDED_ROWS)
        assert rows.count() >= 1, "Expected at least one deal row"
        seen = set()
        for i in range(min(rows.count(), 30)):
            status = rows.nth(i).locator("td").nth(idx["Deal Status"]).inner_text().strip()
            if status:
                seen.add(status.lower())
        assert seen, "No Deal Status values found"
        unexpected = seen - ALLOWED_STATUSES
        assert not unexpected, f"Unexpected Deal Status value(s): {unexpected}"

    @allure.title("TC-77 | Pause Fee rule = Funding Amount × 2.5%")
    def test_pause_fee_formula(self, admin_page):
        ml = MerchantListPage(admin_page)
        ml.goto()
        deal = ml.find_funded_deal()
        calc = DealCalculator(deal["amount_funded"], deal["factor_rate"], 0.0, 0.0)
        expected = round(deal["amount_funded"] * 0.025, 2)
        assert calc.pause_fee() == expected, (
            f"Pause fee for funding {deal['amount_funded']}: "
            f"calc={calc.pause_fee()}, expected={expected}"
        )
